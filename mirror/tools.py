import requests
from datetime import datetime

from llama_index.core.workflow import Context
from llama_index.core.tools import FunctionTool
from llama_index.tools.tavily_research import TavilyToolSpec

from mirror.conf import (
    User,
    CLOUD_MUSIC,
    BILIBILI,
    EDGE,
)
from mirror.plugs import (
    CloudMusicPlugin,
    BilibliPlugin,
    EdgePlugin,
)
from mirror.diary_manager import DiaryManager


####################Diary Generator tools#####################
# 1. Plugin tools and Fetch tool
plugin_tools = []
cloud_music_plugin = CloudMusicPlugin(
    user_id=CLOUD_MUSIC['user_id'],
    MUSIC_U=CLOUD_MUSIC['music_u'],
    csrf=CLOUD_MUSIC['csrf'],
    db=CLOUD_MUSIC['db']
)
cloud_music_tool = cloud_music_plugin.get_tool()
plugin_tools.append(cloud_music_tool)

bilibili_plugin = BilibliPlugin(SESSDATA=BILIBILI['SESSDATA'])
bilibili_tool = bilibili_plugin.get_tool()
plugin_tools.append(bilibili_tool)

edge_plugin = EdgePlugin(
    history_path=EDGE['history_path'],
    mode=EDGE['mode'],
)
edge_tool = edge_plugin.get_tool()
plugin_tools.append(edge_tool)


def get_date_location_weather() -> dict:
    # Today
    today = datetime.now().strftime("%Y-%m-%d")

    # Location from IP address
    ip_response = requests.get('https://ipinfo.io/json')
    location_data = ip_response.json()
    city = location_data.get('city', 'Unknown')
    country = location_data.get('country', 'Unknown')

    # OpenWeatherMap API
    # TODO: Hard code here
    WEATHER_API_KEY = "29e7696c3b1a8c6de55d8ecc2685ae31"
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    weather_data = requests.get(weather_url).json()

    description = weather_data["weather"][0]["description"]
    temp = str(round(weather_data["main"]["temp"] - 273.15, 1)) + "°C"

    return {
        "date": today,
        "location": f"{city}, {country}",
        "weather": f"天气为 {description}，温度为 {temp}",
    }


async def collect_basic_data(ctx: Context) -> str:
    """Useful for collect today's date, user name, location and weather for diary writing."""
    basic_data = get_date_location_weather()
    current_state = await ctx.get("state")

    current_state["user_name"] = User
    current_state["date"] = basic_data['date']
    current_state["location"] = basic_data['location']
    current_state["weather"] = basic_data['weather']

    await ctx.set("state", current_state)
    return "Finish collecting basic data."


async def collect_raw_data(ctx: Context) -> str:
    """Useful for collecting user's raw online behavior data today."""
    raw_data = []
    for tool in plugin_tools:
        tool: FunctionTool
        res = await tool.acall()
        raw_data.append(res)

    state = await ctx.get("state")
    if "raw_behavior" not in state:
        state["raw_behavior"] = []
    state['raw_behavior'] = raw_data
    await ctx.set("state", state)
    return "Finish collecting user's raw online behavior."


# 2. Web search tool from tavily and Record tool
# TODO: rm hardcode
web_search_tool = TavilyToolSpec(api_key="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")
web_search_tool = web_search_tool.to_tool_list()[0]
# BUG (fixed) : original name "search" is invalid for some reason.
web_search_tool.metadata.name = "search_web"
web_search_tool.metadata.description = "search_web" + web_search_tool.metadata.description[6:]


async def data_analysis(ctx: Context, analysis_content: str) -> str:
    """Useful for analyzing user's raw online behavior data today."""
    state = await ctx.get("state")
    if "enhanced_data" not in state:
        state["enhanced_data"] = {}
    state["enhanced_data"]["analysis"] = analysis_content
    await ctx.set("state", state)
    return "Finish analysis."


async def record_enhanced_data(ctx: Context, enhanced_data: str, title: str) -> str:
    """Useful for recording enhanced data into context."""
    state = await ctx.get("state")
    if "enhanced_data" not in state:
        state["enhanced_data"] = {}
    state["enhanced_data"][title] = enhanced_data
    await ctx.set("state", state)
    return "Finish recording enhanced data."


# 3. Write tool
async def write_diary(ctx: Context, diary_content: str) -> str:
    """Useful for writing a diary on user's raw and enhanced online behavior today."""
    current_state = await ctx.get("state")
    current_state["diary_content"] = diary_content
    await ctx.set("state", current_state)
    return "Diary written."


# 4. Review tool
async def review_diary(ctx: Context, review: str) -> str:
    """Useful for reviewing a diary and providing feedback."""
    current_state = await ctx.get("state")
    current_state["review"] = review
    await ctx.set("state", current_state)
    return "Diary reviewed."


####################Diary Summary tools#####################
async def fetch_diary(ctx: Context) -> str:
    """Useful for fetching weekly diary."""
    weekly_diary, cnt = DiaryManager.get_instance().get_weekly_diary()
    if cnt == 0:
        diary_content = "本周没有日记记录。"
    else:
        diary_content = (
            "本周有 " + str(cnt) + " 条日记记录。\n\n"
            "本周的日记内容如下：\n\n" + "\n\n".join(weekly_diary)
        )
    current_state = await ctx.get("state")
    current_state["weekly_diary"] = diary_content
    return diary_content


async def write_diary_summary(ctx: Context, diary_summary: str) -> str:
    """Useful for writing a diary summary."""
    current_state = await ctx.get("state")
    current_state["diary_summary"] = diary_summary
    await ctx.set("state", current_state)
    return "Diary summary written."


async def review_diary_summary(ctx: Context, review: str) -> str:
    """Useful for reviewing a diary summary and providing feedback."""
    current_state = await ctx.get("state")
    current_state["review"] = review
    await ctx.set("state", current_state)
    return "Diary summary reviewed."


####################Diary Chat tools#####################
async def query_diary(ctx: Context, query_text: str) -> str:
    """Useful for query diary content in time range."""
    res = DiaryManager.get_instance().query(query_text)
    current_state = await ctx.get("state")
    current_state["diary_content"] = res
    await ctx.set("state", current_state)
    return "Diary retrieved."
