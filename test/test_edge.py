import os
import shutil
import sqlite3
from datetime import datetime, timedelta

def is_edge_running():
    history_path = '/mnt/c/Users/z1519/AppData/Local/Microsoft/Edge/User Data/Default/History'
    try:
        with open(history_path, 'r'):
            return False
    except IOError:
        return True


def get_edge_history():
    if is_edge_running():
        print("Edge 浏览器正在运行。请关闭浏览器后再尝试访问历史记录文件。")
        return


    history_path = "/mnt/c/Users/z1519/AppData/Local/Microsoft/Edge/User Data/Default/History"


    if not os.path.exists(history_path):
        print("未找到 Edge 浏览器的历史记录文件。")
        return

    temp_history = 'EdgeHistory'
    shutil.copy2(history_path, temp_history)


    conn = sqlite3.connect(temp_history)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(urls);")
    tables = cursor.fetchall()
    print("Tables in the database:", tables)

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
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
        if title not in records:
            records[title] = (visit_time, visit_count, url)
        else:
            records[title] = (records[title][0], records[title][1] + visit_count, url)

    conn.close()
    os.remove(temp_history)
    return records


# res = get_edge_history()

# from pprint import pprint
# pprint(res)

