import requests
from datetime import datetime, timedelta
import json
from pprint import pprint


SESSDATA = "32312fdf%2C1759639214%2Ccfb4a%2A41CjA_nvYVA3fh-SgIBCWcXQpCMEK3_WTKL4lhW3nXRfb6fkj14fIqoUpKbNEiuAjy93ISVm1icHhUQ0QtN2pLNVNuQzBWUUU0VklXZ2ROb24tOGUya3lCQ3hfcXFsS2hwd243em5Tc09hQ1NQMVJXbDdGMlRQRm04V3dWdS1IczMtaWxKdWxXb0JBIIEC"


def get_bilibili_today_history(sessdata: str):
    """通过SESSDATA获取当天B站观看历史

    Args:
        sessdata: 从浏览器Cookie中提取的SESSDATA值

    Returns:
        list: 当天观看记录列表，包含视频标题、UP主、BV号等信息
    """
    # 1. 构造请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": f"SESSDATA={sessdata}",
        "Referer": "https://www.bilibili.com/account/history"
    }

    # 2. 计算今天的时间范围（UTC+8时间戳）
    today = datetime.now()
    start_time = int((today.replace(hour=0, minute=0, second=0)).timestamp())
    end_time = int((today.replace(hour=23, minute=59, second=59)).timestamp())

    # 3. 分页获取历史记录
    history_list = []
    max_id = 0  # 分页游标
    view_at = 0  # 时间戳游标

    while True:
        url = f"https://api.bilibili.com/x/web-interface/history/cursor?max={max_id}&view_at={view_at}&business=archive"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            if data["code"] != 0 or not data.get("data"):
                break

            # 4. 筛选今天的记录
            for item in data["data"]["list"]:
                item_time = item.get("view_at", 0)
                if start_time <= item_time <= end_time:
                    # pprint(item)
                    history_list.append({
                        "title": item.get("title"),
                        "tag": item.get("tag_name"),
                        "author": item.get("author_name"),
                        "bvid": item.get("history", {}).get("bvid"),
                        "watch_time": datetime.fromtimestamp(item_time).strftime("%H:%M"),
                        "duration": str(timedelta(seconds=item.get("duration", 0))),  # 视频时长(秒)
                        "progess": str(timedelta(seconds=item.get("progress", 0))),  # 观看进度
                    })

            # 5. 更新分页参数
            cursor = data["data"]["cursor"]
            if not cursor or view_at == cursor["view_at"]:
                break

            max_id = cursor["max"]
            view_at = cursor["view_at"]

            # 如果记录时间早于今天，终止查询
            if view_at < start_time:
                break

        except Exception as e:
            print(f"请求失败: {str(e)}")
            break

    return history_list


res = get_bilibili_today_history(SESSDATA)
pprint(res)
