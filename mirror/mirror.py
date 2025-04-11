from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.schema import Document

from mirror.agents import (
    fetch_agent,
    websearch_and_record_agent,
    write_diary_agent,
    review_diary_agent,
)
from mirror.utils import (
    danger_print,
    warning_print,
    success_print,
    get_date_location_weather,
    iso_date,
    save_diary,
    get_index,
    insert_diary_to_index,
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
def diary_generator(
    save: bool = True,
    add_to_index: bool = True,
    verbose: bool = False
):
    r"""Run the diary generator workflow to generate a diary.

    Args:
        save (bool): Whether to save the diary to local file.
            (default: True)
        add_to_index (bool): Whether to add the diary to the index.
            (default: False)
        verbose (bool): Whether to print detailed information into cmd.
            (default: False)
    """
    if verbose:
        print("🚀 Starting the diary generator workflow...")
    prompt = (
        "你是一个日记写作助手，你将通过我的上网行为来帮我撰写今天的日记。"
        "任务：帮我写一篇我今天网络行为的总结性日记。"
    )
    handler = workflow_1.run(user_msg=prompt)
    state = handler.ctx.get("state")

    today = state.get("date", "No date provided.")
    if today == "No date provided.":
        today = get_date_location_weather()['date']
        if verbose:
            warning_print("⚠️ No date provided in state after diary generator workflow.")

    diary_content = state.get("diary_content", "No diary content generated.")
    if diary_content == "No diary content generated." and verbose:
        danger_print("❗ No diary content generated in state after diary generator workflow.")

    if verbose:
        print(f"📖 Diary Content: {diary_content}")

    if save:
        save_diary(diary_content, file_name=f"diary_{today}.md")
        if verbose:
            success_print("💾 Diary saved to local file.")

    if add_to_index:
        diary_doc = Document(
            text=diary_content,
            metadata={
                "date": iso_date(today),
                "location": state.get("location", "No location provided."),
                "weather": state.get("weather", "No weather data provided."),
            },
        )
        index = get_index(force_load=False)
        insert_diary_to_index(index, diary_doc)
        if verbose:
            success_print("📚 Diary content added to the index.")


# test code
if __name__ == "__main__":
    # from mirror.utils import cmdoutput_agent_workflow1
    # prompt = (
    #     "你是一个日记写作助手，你将通过我的上网行为来帮我撰写今天的日志"
    #     "帮我写一篇我今天的总结性日记。"
    # )

    # import asyncio
    # asyncio.run(cmdoutput_agent_workflow1(
    #     workflow=workflow_1,
    #     prompt=prompt,
    # ))
    diary_generator(save=True, add_to_index=True, verbose=True)
