from typing import Optional
import asyncio

from llama_index.core import Settings

from mirror.types import VerboseLevel
from mirror.utils import (
    success_print,
    danger_print,
    async_run_workflow
)
from mirror.models import openai_like_llm, bge_embedding_model
from mirror.workflow import workflow_1, workflow_2
from mirror.diary_manager import DiaryManager


def diary_generator(
    diary_manager: DiaryManager,
    save: bool = True,
    verbose: bool = False,
    verbose_level: VerboseLevel = VerboseLevel.LOW,
):
    r"""Run the diary generator workflow to generate a diary.
    """
    if verbose:
        print("🚀 Starting the diary generator workflow...")
    prompt = (
        "你是一个完全自动不需要用户介入的日记写作助手，你将通过我的上网行为来帮我撰写今天的日记。"
        "任务：帮我写一篇我今天网络行为的总结性日记。"
    )
    # handler = workflow_1.run(user_msg=prompt)
    state = asyncio.run(
        async_run_workflow(
            workflow=workflow_1,
            prompt=prompt,
            prompt_args=None,
            verbose=verbose if verbose_level == VerboseLevel.HIGH else False,
        )
    )

    diary_content = state.get("diary_content", "No diary content generated.")
    if diary_content == "No diary content generated." and verbose:
        danger_print("❗ No diary content generated in state after diary generator workflow.")
        return

    if verbose:
        success_print("📝 Diary content generated successfully.")
        print(f"📖 Diary Content: {diary_content}")

    if save:
        diary_manager.add_diary(
            content=diary_content
        )
        if verbose:
            success_print("📚 Diary content added to the index.")


def weekly_diary_summary(
    save_path: Optional[str] = None,
    verbose: bool = False,
    verbose_level: VerboseLevel = VerboseLevel.LOW,
):
    r"""Generate a weekly diary summary.
    """
    if verbose:
        print("🚀 Starting the weekly diary summary workflow...")
    prompt = (
        "你是一个不需要用户介入的日记总结助手，你将获取我本周的日记内容，并根据日记内容生成一篇总结。"
        "任务：帮我总结上周的日记。"
    )

    state = asyncio.run(
        async_run_workflow(
            workflow=workflow_2,
            prompt=prompt,
            prompt_args=None,
            verbose=verbose if verbose_level == VerboseLevel.HIGH else False,
        )
    )

    summary = state.get("diary_summary", "No diary_summary generated.")
    if (summary == "No diary_summary generated."
        or summary == "No summary content.") and verbose:
        danger_print("❗ No diary_summary generated in state after diary summary workflow.")
        return

    if verbose:
        success_print("📝 Diary summary generated successfully.")
        print(f"📖 Diary Summary: {summary}")

    if save_path:
        with open(save_path, "w") as f:
            f.write(summary)
        if verbose:
            success_print(f"📚 Diary summary saved to {save_path}.")


def main(mode=2):
    # Llama index Settings
    Settings.llm = openai_like_llm()
    Settings.embed_model = bge_embedding_model()

    # Initialize the diary manager
    diary_manager = DiaryManager.get_instance()  # Singleton instance

    if mode == 1:
        # Run the diary generator workflow
        diary_generator(
            diary_manager=diary_manager,
            save=True,
            verbose=True,
            verbose_level=VerboseLevel.HIGH,
        )

    elif mode == 2:
        # Generate a weekly diary summary
        weekly_diary_summary(
            save_path="weekly_diary_summary.md",
            verbose=True,
            verbose_level=VerboseLevel.HIGH,
        )


if __name__ == "__main__":
    main(2)
