import os
import sqlite3
import shutil
from datetime import datetime, timedelta
from pydantic import BaseModel

from llama_index.core.tools import FunctionTool, ToolMetadata

from mirror.plugs.base import BasePlugin
from mirror.utils import danger_print, warning_print


class EdgePlugin(BasePlugin):
    prompt_head = "用户今天的 Edge 浏览器历史记录：\n"
    prompt_tail = "用户今天共浏览了{count}个网页。\n"
    def __init__(
        self,
        history_path: str,
        mode: str,
        *,
        temp_path: str = './EdgeHistory',
    ):
        self.history_path = history_path
        self.mode = mode
        self.temp_path = temp_path

    def _is_his_readable(self):
        if not os.path.exists(self.history_path):
            danger_print("History file does not exist.")
            return False
        try:
            with open(self.history_path, 'r'):
                return True
        except IOError:
            danger_print("History file is not accessible.")
            return False

    def _get_today_history(self):
        r"""Returns a dict of (title: visit_time, visit_count, url) for today."""
        if not self._is_his_readable():
            return
        shutil.copy2(self.history_path, self.temp_path)

        conn = sqlite3.connect(self.temp_path)
        cursor = conn.cursor()

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)
        epoch_start = datetime(1601, 1, 1)
        today_start_us = int((today_start - epoch_start).total_seconds() * 1_000_000)
        tomorrow_start_us = int((tomorrow_start - epoch_start).total_seconds() * 1_000_000)
        cursor.execute("""
            SELECT title, last_visit_time, visit_count, url FROM urls
            WHERE last_visit_time BETWEEN ? AND ?
            ORDER BY last_visit_time DESC
        """, (today_start_us, tomorrow_start_us))
        rows = cursor.fetchall()
        records = {}
        for title, last_visit_time, visit_count, url in rows:
            visit_time = datetime(1601, 1, 1) + timedelta(microseconds=last_visit_time)
            visit_time = visit_time.strftime("%H:%M")
            if title not in records:
                records[title] = (visit_time, visit_count, url)
            else:
                records[title] = (visit_time, visit_count + records[title][1], url)
        conn.close()
        os.remove(self.temp_path)
        return records

    async def get_prompt(self) -> str:
        records = self._get_today_history()
        if len(records) > 10:
            records = dict(list(records.items())[:10])
            warning_print("Today's Edge history exceeds 10 records, only use first 10.")
        prompt = self.prompt_head
        if not records:
            warning_print("No Edge history records found.")
            prompt += "今天没有浏览记录。\n"
            return prompt
        for title, (visit_time, visit_count, url) in records.items():
            prompt += f"网站名称: {title}, "
            prompt += f"访问时间: {visit_time}, "
            prompt += f"访问次数: {visit_count}, "
            prompt += f"访问链接: {url}\n"
        prompt += self.prompt_tail.format(count=len(records))
        return prompt

    def get_tool(self) -> str:

        class EdgeToolSchema(BaseModel):
            pass

        metadata = ToolMetadata(
            name="edge_history",
            description="获取用户今天的 Edge 浏览器历史记录",
            fn_schema=EdgeToolSchema,
        )

        return FunctionTool(
            fn=self.get_prompt,
            metadata=metadata,
        )
