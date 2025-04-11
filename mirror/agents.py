from llama_index.core.agent.workflow import FunctionAgent

from mirror.models import openai_like_llm, bge_embedding_model
from mirror.tools import (
    collect_basic_data,
    collect_raw_data,
    web_search_tool,
    record_enhanced_data,
    write_diary,
    review_diary)


llm = openai_like_llm()
embed_model = bge_embedding_model()


####################Diary Generator agents#####################
# 1.
fetch_agent = FunctionAgent(
    name="CollectRawDataAgent",
    description="用于获取和收集用户今天的上网行为信息。",
    system_prompt=(
        "你是一个日志原始素材收集助手。你的任务是：\n"
        "收集日记写作基本信息，例如今天的日期、地点、天气。"
        "收集用户今天在各平台的原始上网行为信息。"
    ),
    llm=llm,
    tools=[collect_basic_data, collect_raw_data],
    can_handoff_to=["WebsearchAndRecordAgent"],
)


# 2.
websearch_and_record_agent = FunctionAgent(
    name="WebsearchAndRecordAgent",
    description="用于根据用户的今日上网行为信息进行 Web 搜索，并将搜索结果记录到上下文状态。",
    system_prompt=(
        "你是一个具有网络搜集功能的文本增强和记录助手。你的任务是：\n"
        "从state['raw_behavior']获取用户今天的上网行为信息，在需要的时候，进行 Web 搜索，"
        "并将搜索到的结果进行理解和整理得到增强后的数据，"
        "然后将增强数据使用工具记录到上下文状态。\n"
        "注意：\n"
        "你只能调用2次网络搜索工具。\n"
    ),
    llm=llm,
    tools=[web_search_tool, record_enhanced_data],
    can_handoff_to=["WriteDiaryAgent"],
)


# 3.
write_diary_agent = FunctionAgent(
    name="WriteDiaryAgent",
    description="用于根据用户的今天的上网行为写一个日记。",
    system_prompt=(
        "你是一个个人日记书写助手。你的任务是：\n"
        "根据在state['raw_behavior']中的用户今天的上网的原始行为信息，"
        "和在state['enhanced_data']中的经过网络搜索的增强信息，写一个个人日记。"
        "注意：\n"
        "日记应该是markdown格式，包含标题、今天的日期（用户会提供）、正文和标签。\n"
        "生成日记后应该调用工具将生成的日记内容存储到上下文状态中。\n"
        "日记写完后，你应该至少获得过来自ReviewAgent的一次反馈才能正式完成。\n"
        "反馈信息在state['review']中，你需要根据反馈信息『修改日记』或者『完成』。\n"
    ),
    llm=llm,
    tools=[write_diary],
    can_handoff_to=["ReviewAgent", "ResearchAgent"],
)


# 4.
review_diary_agent = FunctionAgent(
    name="ReviewAgent",
    description="用于评估一篇日记并提供反馈。",
    system_prompt=(
        "你是一个日记评估助手。你的任务是：\n"
        "根据在state['diary_content']中的用户今天的日记内容，"
        "和在state['raw_behavior']中的用户今天的上网的原始行为信息，"
        "和在state['enhanced_data']中的经过网络搜索的增强信息。\n"
        "评估这篇日记的内容是否准确和完整，"
        "并提供反馈信息。\n"
        "你提供的反馈信息应该要么是对日记内容的『修改建议』，要么是对日记内容的『完成确认』。\n"
        "生成反馈信息后，应该调用工具将生成的反馈信息存储到上下文状态中。\n"
    ),
    llm=llm,
    tools=[review_diary],
    can_handoff_to=["WriteDiaryAgent"],
)


####################Diary Summary agents#####################
# diary_summary_agent = FunctionAgent(
#     name="DiarySummaryAgent",
#     description="用于根据用户的历史日记内容进行总结。",
#     system_prompt=(
#         "你是一个个人日记总结助手。你的任务是：\n"
#         ""
#     ),
#     llm=llm,
#     tools=[],
# )
