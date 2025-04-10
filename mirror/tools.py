from llama_index.core.workflow import Context
from llama_index.core.tools import FunctionTool
from llama_index.tools.tavily_research import TavilyToolSpec

from mirror.conf import CLOUD_MUSIC, User
from mirror.plugs import CloudMusicPlugin
from mirror.utils import get_date_location_weather


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


def collect_basic_data(ctx: Context) -> str:
    """Useful for collect today's date, user name, location and weather for diary writing."""
    basic_data = get_date_location_weather()
    current_state = ctx.get("state")

    current_state["user_name"] = User
    current_state["date"] = basic_data['date']
    current_state["location"] = basic_data['location']
    current_state["weather"] = basic_data['weather']

    ctx.set("state", current_state)
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
