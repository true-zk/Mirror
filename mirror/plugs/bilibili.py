import requests
from datetime import datetime, timedelta
from pydantic import BaseModel

from llama_index.core.tools import FunctionTool, ToolMetadata

from mirror.plugs.base import BasePlugin
from mirror.utils import danger_print, warning_print


class BilibliPlugin(BasePlugin):
    url = "https://api.bilibili.com/x/web-interface/history/cursor?max={max_id}&view_at={view_at}&business=archive"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": "SESSDATA={sessdata}",
        "Referer": "https://www.bilibili.com/account/history"
    }
    prompt_head = "用户今天的Bilibili观看记录如下：\n"
    prompt_tail = "用户今天共观看了{count}个视频。\n"


    def __init__(self, SESSDATA: str):
        self.SESSDATA = SESSDATA
        self.headers["Cookie"] = self.headers["Cookie"].format(sessdata=self.SESSDATA)

    def _fetch_parse_today_his(self):
        today = datetime.now()
        start_time = int((today.replace(hour=0, minute=0, second=0)).timestamp())
        end_time = int((today.replace(hour=23, minute=59, second=59)).timestamp())

        history_l = []
        max_id = 0  # Page cursor
        view_at = 0  # Time cursor

        while True:
            url = self.url.format(max_id=max_id, view_at=view_at)
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                data = response.json()
            except Exception as e:
                danger_print(f"Error fetching data: {e}")
                break

            if data["code"] != 0 or not data.get("data"):
                break

            # Filter today's records
            for item in data["data"]["list"]:
                item_time = item.get("view_at", 0)
                if start_time <= item_time <= end_time:
                    history_l.append({
                        "title": item.get("title"),
                        "tag": item.get("tag_name"),
                        "author": item.get("author_name"),
                        "bvid": item.get("history", {}).get("bvid"),
                        "watch_time": datetime.fromtimestamp(item_time).strftime("%H:%M"),
                        "duration": str(timedelta(seconds=item.get("duration", 0))),
                        "progess": str(timedelta(seconds=item.get("progress", 0))),
                    })

            # Update pagination parameters
            cursor = data["data"]["cursor"]
            if not cursor or view_at == cursor["view_at"]:
                break

            max_id = cursor["max"]
            view_at = cursor["view_at"]

            # If the record time is earlier than today, terminate the query
            if view_at < start_time:
                break

        return history_l

    async def get_prompt(self) -> str:
        r"""Get today's Bilibili watch history."""
        def _gen_prompt(history_list: list) -> str:
            prompt = self.prompt_head
            for item in history_list:
                prompt += f"🎥 第1个视频: "
                prompt += f"标题: {item['title']}, "
                prompt += f"标签: {item['tag']}, "
                prompt += f"作者: {item['author']}, "
                prompt += f"观看时间: {item['watch_time']}, "
                prompt += f"视频时长: {item['duration']}, "
                prompt += f"观看进度: {item['progess']}\n"
                prompt += f"链接: https://www.bilibili.com/video/{item['bvid']}\n\n"
            prompt += self.prompt_tail.format(count=len(history_list))
            return prompt

        history_list = self._fetch_parse_today_his()
        if len(history_list) > 10:
            history_list = history_list[:10]
            warning_print("Today's Bilibili watch history exceeds 10 records, only use first 10.")
        if not history_list:
            warning_print("No Bilibili watch history today.")
            return "No Bilibili watch history today."

        return _gen_prompt(history_list)

    def get_tool(self) -> str:

        class BilibiliToolSchema(BaseModel):
            pass

        metadata = ToolMetadata(
            name="get_today_bilibili_watch_record",
            description="获取用户今天的Bilibili观看记录",
            fn_schema=BilibiliToolSchema,
        )

        return FunctionTool(
            fn=self.get_prompt,
            metadata=metadata,
        )
