from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel
import requests
import pandas as pd
import sqlite3

from llama_index.core.tools import FunctionTool, ToolMetadata

from mirror.plugs.base import BasePlugin
from mirror.utils import danger_print, warning_print


class CloudMusicPlugin(BasePlugin):
    url = "https://music.163.com/api/v1/play/record"
    day_table = "day_history"
    week_table = "week_history"
    prompt_head = "用户今天的网易云音乐听歌记录如下：\n"
    prompt_tail = "用户今天共听了{count}首歌。\n"

    def __init__(
        self,
        user_id: str,
        MUSIC_U: str,
        csrf: str,
        db: str = "cloud_music.db"
    ):
        self.db = db
        self.user_id = user_id
        self.MUSIC_U = MUSIC_U
        self.csrf = csrf
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://music.163.com/"
        }
        self.cookies = {
            "MUSIC_U": self.MUSIC_U,
            "__csrf": self.csrf
        }

        self.conn = self._init_db()

    def _init_db(self) -> None:
        """Create the SQLite database and table if they do not exist."""
        create_table_sql1 = f"""
        CREATE TABLE IF NOT EXISTS {self.day_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            play_count INTEGER DEFAULT 1,
            record_date DATE NOT NULL,
            UNIQUE(song_id, record_date)  -- Avioid duplicate entries on the same day
        );
        CREATE INDEX IF NOT EXISTS idx_date ON {self.day_table}(record_date);
        CREATE INDEX IF NOT EXISTS idx_song ON {self.day_table}(song_id);
        """

        create_table_sql2 = f"""
        CREATE TABLE IF NOT EXISTS {self.week_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            play_count INTEGER DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_song ON {self.week_table}(song_id);
        """

        try:
            with sqlite3.connect(self.db) as conn:
                conn.executescript(create_table_sql1)
                conn.executescript(create_table_sql2)
                conn.commit()
        except sqlite3.Error as e:
            danger_print(f"DB init error: {e}")
            raise

    def _save_to_day_table(self, df: pd.DataFrame) -> int:
        """Save the DataFrame to the SQLite database."""
        insert_sql = f"""
        INSERT OR REPLACE INTO {self.day_table}
        (song_id, name, artist, album, play_count, record_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        try:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                count = cursor.executemany(
                    insert_sql,
                    df[["song_id", "name", "artist", "album",
                        "play_count", "record_date"]].values.tolist()
                ).rowcount
                conn.commit()
                return count
        except sqlite3.Error as e:
            danger_print(f"Failed to insert: {e}")
            return 0

    def _check_update_total_his(self, record: Dict) -> int:
        """Check if the song ID exists in the week history table.
        If so, increment the play count. Else insert a new record.

        Returns:
            int: 0 if not today, >0 if today, -1 if error
        """
        song_id = record["song"]["id"]
        cnt = record["playCount"]
        query = f"""
        SELECT play_count FROM {self.week_table}
        WHERE song_id = ?
        """
        try:
            with sqlite3.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (song_id,))
                result = cursor.fetchone()
                if result:
                    if result[0] == cnt:
                        return 0  # Not today record
                    else:
                        new_cnt = cnt
                        update_sql = f"""
                        UPDATE {self.week_table}
                        SET play_count = ?
                        WHERE song_id = ?
                        """
                        cursor.execute(update_sql, (new_cnt, song_id))
                        conn.commit()
                        return cnt - result[0]  # Return today record count
                else:
                    insert_sql = f"""
                    INSERT INTO {self.week_table}
                    (song_id, name, artist, album, play_count)
                    VALUES (?, ?, ?, ?, ?)
                    """
                    cursor.execute(
                        insert_sql,
                        (
                            song_id,
                            record["song"]["name"],
                            ", ".join([ar["name"] for ar in record["song"]["ar"]]),
                            record["song"]["al"]["name"],
                            cnt
                        )
                    )
                    conn.commit()
                    return cnt  # Return today record count
        except sqlite3.Error as e:
            danger_print(f"DB error: {e}")
            return -1

    def _get_weekly_records(self) -> Dict:
        r"""Retrieve the weekly play records from the API."""
        params = {
            "uid": self.user_id,
            "type": "1",
        }
        response = requests.get(
            self.url,
            params=params,
            headers=self.headers,
            cookies=self.cookies
        )
        return response.json()

    def _parse_daily_records(self) -> None:
        """Parse the daily records from the weekly records."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_songs = []

        for record in self._get_weekly_records().get("weekData", []):
            if (cnt := self._check_update_total_his(record)) > 0:
                song_info = {
                    "song_id": record["song"]["id"],
                    "name": record["song"]["name"],
                    "artist": ", ".join([ar["name"] for ar in record["song"]["ar"]]),
                    "album": record["song"]["al"]["name"],
                    "play_count": cnt,
                    "record_date": today
                }
                daily_songs.append(song_info)

        if daily_songs:
            df = pd.DataFrame(daily_songs)
            agg_df = df.groupby(
                ["song_id", "name", "artist", "album", "record_date"]
            ).agg(
                {
                "play_count": "sum",
                }
            ).reset_index()
            self._save_to_day_table(agg_df)
        else:
            warning_print("Warning: No new records to save.")

    # Test functions
    def query_records(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        top_n: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Query the play records from the database.

        Args:
            start_date (str): The start date in YYYY-MM-DD format.
            end_date (Optional[str]): If None, only query start data.
            top_n (Optional[int]): The number of top songs to retrieve.
        """
        query_sql = """
        SELECT
            song_id, name, artist, album,
            SUM(play_count) as total_plays
        FROM {table}
        WHERE record_date >= ?
        {end_date_condition}
        GROUP BY song_id, name, artist, album
        {order_by}
        {limit}
        """

        params = [start_date]
        conditions = []

        if end_date:
            conditions.append("AND record_date <= ?")
            params.append(end_date)

        order_by = "ORDER BY total_plays DESC"
        limit = f"LIMIT {top_n}" if top_n else ""

        query_sql = query_sql.format(
            table=self.day_table,
            end_date_condition=" ".join(conditions),
            order_by=order_by,
            limit=limit
        )

        try:
            with sqlite3.connect(self.db) as conn:
                df = pd.read_sql(query_sql, conn, params=params)
                return df
        except sqlite3.Error as e:
            print(f"Query error: {e}")
            return pd.DataFrame()

    def get_today_top_songs(self, n: int = 5) -> List[Dict]:
        """Get today's top N songs."""
        today = datetime.now().strftime("%Y-%m-%d")
        df = self.query_records(today, top_n=n)
        return df.to_dict("records")

    # Base Plugin functions ###################################
    async def get_prompt(self) -> str:
        """获取今天的听歌记录，并写成一个LLM可以理解的格式
        会先调用 _parse_daily_records() 来更新数据库"""
        def _gen_prompt(records: list) -> str:
            prompt = self.prompt_head
            for i, record in enumerate(records):
                prompt += f"第{i+1}首："
                prompt += f"歌曲：{record['name']} "
                prompt += f"歌手：{record['artist']} "
                prompt += f"专辑：{record['album']} "
                prompt += f"播放次数：{record['play_count']} \n"
            prompt += self.prompt_tail.format(count=len(records))
            return prompt

        self._parse_daily_records()
        today = datetime.now().strftime("%Y-%m-%d")
        query = f"""
        SELECT
            name, artist, album, play_count
        FROM {self.day_table}
        WHERE record_date = ?
        """
        params = [today]
        try:
            with sqlite3.connect(self.db) as conn:
                df = pd.read_sql(query, conn, params=params)
                if not df.empty:
                    records = df.to_dict("records")
                    return _gen_prompt(records)
                else:
                    warning_print("Cloud music: No records found for today.")
                    return "用户今天没有听歌记录。\n"
        except sqlite3.Error as e:
            danger_print(f"Query error: {e}")
            return ""

    def get_tool(self) -> FunctionTool:

        class CloudMusicSchema(BaseModel):
            pass

        metadata = ToolMetadata(
            name="get_today_cloud_music_listening_record",
            description="用于获取用户今天的网易云音乐听歌记录",
            fn_schema=CloudMusicSchema
        )
        return FunctionTool(
            fn=self.get_prompt,
            metadata=metadata
        )
