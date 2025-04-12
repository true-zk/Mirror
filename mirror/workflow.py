from llama_index.core.agent.workflow import AgentWorkflow


# Workflow 1: 日记写作助手
from mirror.agents import (
    fetch_agent,
    websearch_and_record_agent,
    write_diary_agent,
    review_diary_agent,
)

agents_for_workflow_1 = [
    fetch_agent,
    websearch_and_record_agent,
    write_diary_agent,
    review_diary_agent,
]

workflow_1 = AgentWorkflow(
    agents=agents_for_workflow_1,
    root_agent=fetch_agent.name,
    initial_state={
        "user_name": "",
        "date": "",
        "location": "",
        "weather": "",
        "raw_behavior": [],
        "enhanced_data": {},
        "diary": "Not written yet.",
        "review": "Review required.",
    },
    state_prompt=(
        "你是一个个人日记写作助手，"
        "你将根据当前的上下文信息帮助用户完成日记写作任务。\n\n"
        "当前状态信息：{state}，具体来说：\n"
        "📅 日期：{state[date]}\n"
        "🧑 用户：{state[user_name]}\n"
        "📍 地点：{state[location]}\n"
        "🌤️ 天气：{state[weather]}\n"
        "📝 行为记录：{state[raw_behavior]}\n"
        "🔍 增强数据：{state[enhanced_data]}\n"
        "📖 日记内容：{state[diary]}\n"
        "🔍 反馈信息：{state[review]}\n"
        "💬 用户请求信息：{msg}\n\n"
        "请开始。"
    )
)


# Workflow 2: 日记总结助手
from mirror.agents import (
    diary_summary_agent,
    diary_summary_revirew_agent,
)

agents_for_workflow_2 = [diary_summary_agent, diary_summary_revirew_agent]


workflow_2 = AgentWorkflow(
    agents=agents_for_workflow_2,
    root_agent=diary_summary_agent.name,
    initial_state={
        "weekly_diary": "No diary content.",
        "diary_summary": "No summary content.",
        "review": "Review required.",
    },
    state_prompt=(
        "你是一个个人日记总结助手，"
        "你将根据当前的上下文信息帮助用户完成总结任务。\n\n"
        "当前状态信息在：{state}，具体来说：\n"
        "本周日记内容 weekly_diary：{state[weekly_diary]}\n"
        "日记总结 diary_summary：{state[diary_summary]}\n"
        "总结的反馈 review：{state[review]}\n"
        "💬 用户请求信息：{msg}\n\n"
        "请开始。"
    )
)
