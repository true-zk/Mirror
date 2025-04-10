# from tavily import TavilyClient
# tavily_client = TavilyClient(api_key="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")
# response = tavily_client.search("Who is Leo Messi?")
# print(response)


from llama_index.tools.tavily_research import TavilyToolSpec

web_search_tool = TavilyToolSpec(api_key="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")
web_search_tool = web_search_tool.to_tool_list()[0]
# BUG (fixed) : original name "search" is invalid for some reason.
web_search_tool.metadata.name = "search_web"
web_search_tool.metadata.description = "search_web" + web_search_tool.metadata.description[6:]


prompt = (
    "请根据提供的用户听歌记录或Bilibi视频观看记录，搜索相关的背景资料，并增强原始素材。"
    "请注意，增强的内容应该与原始素材相关，并提供更多的信息和背景资料。"
    "例如：如果用户今天在网易云听了一首歌，你可以搜索这首歌的介绍、歌词、MV等相关信息，并将这些信息添加到原始素材中。"
    "如果用户今天在B站观看了一段视频，你可以搜索这段视频的简介、评论、弹幕等相关信息，并将这些信息添加到原始素材中。"
    "请确保增强的内容是准确和有用的，并且与原始素材相关。"
    "对于用户的每条听歌记录或视频观看记录请返回较为简洁的结果。"
)


prompt += (
    "用户今天的听歌记录："
    "第1首：歌曲：Die For You 歌手：The Weeknd 专辑：Starboy 播放次数：1 "
    "第2首：歌曲：Gimme! Gimme! Gimme! (A Man After Midnight) 歌手：ABBA 专辑：ABBA Gold: Greatest Hits 播放次数：1 "
)


async def test():
    res = await web_search_tool.acall(prompt)
    print(res)

import asyncio
asyncio.run(test())