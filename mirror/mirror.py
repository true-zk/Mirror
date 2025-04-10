from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.schema import Document

from mirror.agents import (
    fetch_agent,
    websearch_and_record_agent,
    write_diary_agent,
    review_diary_agent,
)


# Workflow 1: 日记写作助手
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
        "📝 行为记录：{state[diary]}\n\n"
        "💬 用户请求信息：{msg}\n\n"
        "请开始。"
    )
)


# Workflow 2: 日记总结助手
agents_for_workflow_2 = []


workflow_2 = AgentWorkflow(
    agents=agents_for_workflow_2,
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
        "你是一个个人日记总结助手，"
        "你将根据当前的上下文信息帮助用户完成总结任务。\n\n"
        "当前状态信息：{state}，具体来说：\n"
        "📅 日期：{state[date]}\n"
        "🧑 用户：{state[user_name]}\n"
        "📍 地点：{state[location]}\n"
        "🌤️ 天气：{state[weather]}\n"
        "📝 行为记录：{state[diary]}\n\n"
        "💬 用户请求信息：{msg}\n\n"
        "请开始。"
    )
)


# Main function
def diary_generator(verbose: bool = False):
    if verbose:
        print("🚀 Starting the diary generator workflow...")
    prompt = (
        "你是一个日记写作助手，你将通过我的上网行为来帮我撰写今天的日记。"
        "任务：帮我写一篇我今天网络行为的总结性日记。"
    )
    handler = workflow_1.run(user_msg=prompt)
    state = handler.ctx.get("state")
    diary_content = state.get("diary_content", "No diary content generated.")
    if verbose:
        print(f"📖 Diary Content: {diary_content}")
    diary_doc = Document(
        text=diary_content,
        metadata={
            "date": state.get("date", "No date provided."),
            "location": state.get("location", "No location provided."),
            "weather": state.get("weather", "No weather data provided."),
        },
    )





# test code
if __name__ == "__main__":
    from mirror.utils import cmdoutput_agent_workflow1
    prompt = (
        "你是一个日记写作助手，你将通过我的上网行为来帮我撰写今天的日志"
        "帮我写一篇我今天的总结性日记。"
    )

    import asyncio
    asyncio.run(cmdoutput_agent_workflow1(
        workflow=workflow_1,
        prompt=prompt,
    ))
