import requests
from pprint import pprint
from datetime import datetime
import json

# def get_netease_history(user_id, music_u, csrf):
#     url = "https://music.163.com/api/v1/play/record"
#     params = {"uid": user_id, "type": "0", "limit": "100"}
#     headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"}
#     cookies = {"MUSIC_U": music_u, "__csrf": csrf}

#     try:
#         response = requests.get(url, params=params, headers=headers, cookies=cookies)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"请求失败，状态码：{response.status_code}")
#             return None
#     except Exception as e:
#         print(f"发生错误：{e}")
#         return None


# 使用示例
if __name__ == "__main__":

    user_id="372411683"
    music_u="00F1ABD600CC1AEE1CF6CE73D87CD131CF2D6AD4667089FB668663BE4DB516AABBCA3EEA7374EC1365EDAEAF210FFA6B2FCDC5ECE85B8E70D3784AD8533FCEC68F3097361B8097BE461ABCCA1E20885F5D3C37CDC0A7ED126CB61D47CC020719FF60EFD4049C1AD95C322F71BC9191D9957EE5E787286669A07EFAB41638ACDAFF2AAC77AEAD92AAA75B30BBAD9237220AD35411706EF55E6DE97A876A3CADD7D2AF0538E86E28E05FF683F5BB3EA30A052F3B164F45C0AE367170589F41890E0E5957C7D76E4E903305AA6E6B6B63A241F46D701AEF71D4CA89908714F990D3C40E9575F47D1183ACE81B627230D465B159C0B475D522BCD5BE1C206F3DCF714ADF3D4C68DC13010AB66E282BB619899BDFAA6B2112D3DB278127C19641866E9FDB3A8E6FFA93585826B085421F7474AECF39B068DBB738BAA5E626A3F881C48DC7ABD27CA6AAF25663C653B9204E8D60C37C1087236C9F438564E0411ED0370CA175002246185D6BDC34BD0304C72E142D8EC5F4E0A6542C39EDBBA7B6FE07D5"
    csrf="3a5df4d81cde9da83e9708300754bf17"

    url = "https://music.163.com/api/v1/play/record"

    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"}
    cookies = {"MUSIC_U": music_u, "__csrf": csrf}

    params = {
        "uid": "372411683",
        "type": "1",  # 1=最近一周
        # "limit": "1"
    }
    # 其他参数同上
    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    response.json()

    data = response.json()  # 先获取一周数据
    with(open("netease.json", "w", encoding="utf-8") as f):
        json.dump(data, f, ensure_ascii=False, indent=4)
    # today = datetime.now().strftime("%Y-%m-%d")

    # today_songs = []
    # for song in data["weekData"]:
    #     if song["playTime"].startswith(today):
    #         today_songs.append({
    #             "name": song["song"]["name"],
    #             "artist": song["song"]["ar"][0]["name"],
    #         })
    # pprint(today_songs)

