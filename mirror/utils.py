import os
import re
import dateparser.search
import dateparser
from typing import Optional, Tuple
from functools import partial
from datetime import datetime, timedelta
from pprint import pprint
from colorama import Fore, Style

from llama_index.core.agent.workflow import (
    AgentWorkflow,
    AgentOutput,
    ToolCallResult,
    ToolCall,
    )


# Basic utils
def print_color(text: str, color: str = "green") -> None:
    r"""Print text in color."""
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
    }
    print(colors.get(color, Fore.WHITE) + text + Style.RESET_ALL)


danger_print = partial(print_color, color="red")
warning_print = partial(print_color, color="yellow")
success_print = partial(print_color, color="green")


def extract_date_range_from_prompt(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    """
    自动从 prompt 中提取自然语言日期范围，并转换为 "YYYY-MM-DD" 格式
    """
    # Normalize
    prompt = prompt.lower().strip()
    start_dt = datetime(1601, 1, 1)
    end_dt = datetime.now()

    # Match 形式：从XX到XX / XX到XX
    match = re.search(r"(从)?(.+?)(到|至)(.+?)(的)?", prompt)
    if match:
        start_expr = match.group(2).strip()
        end_expr = match.group(4).strip()
        start_dt = dateparser.parse(start_expr)
        end_dt = dateparser.parse(end_expr)
        if start_dt and end_dt:
            return (
                start_dt.strftime("%Y-%m-%d"),
                end_dt.strftime("%Y-%m-%d"),
            )

    # 单点日期，如“昨天”、“今天”、“三天前”
    single_expr = re.search(r"(本周|这周|这星期|今天|今天之前|之前|昨天|前天|上周|上星期|上个月|最近几天|几天前|几天内|过去几天|最近)", prompt)
    if single_expr:
        base_dt = datetime.now()
        expr = single_expr.group(1)

        if expr in ["昨天"]:
            dt = base_dt.replace(hour=0, minute=0, second=0) - timedelta(days=1)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d")

        if expr in ["今天"]:
            dt = base_dt.replace(hour=0, minute=0, second=0)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d")

        if expr in ["今天之前", "之前"]:
            dt = base_dt.replace(hour=0, minute=0, second=0)
            return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")

        if expr in ["本周", "这周", "这星期"]:
            start = base_dt - timedelta(days=base_dt.weekday())
            end = start + timedelta(days=7)
            return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

        if expr in ["上周", "上星期"]:
            start = base_dt - timedelta(days=base_dt.weekday() + 7)
            end = start + timedelta(days=6)
            return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

        if expr in ["上个月"]:
            first_day_this_month = base_dt.replace(day=1)
            last_month_end = first_day_this_month - timedelta(days=1)
            start = last_month_end.replace(day=1)
            return start.strftime("%Y-%m-%d"), last_month_end.strftime("%Y-%m-%d")

        if expr in ["最近几天", "几天前", "几天内", "过去几天"]:
            end = base_dt
            start = base_dt - timedelta(days=3)
            return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    # 全局自然语言 parse
    parsed = dateparser.search.search_dates(prompt, settings={"RELATIVE_BASE": datetime.now(), "PREFER_DATES_FROM": "past"})
    if parsed:
        parsed_dates = sorted([dt for _, dt in parsed])
        start = parsed_dates[0].strftime("%Y-%m-%d")
        end = parsed_dates[-1].strftime("%Y-%m-%d")
        return start, end

    return None, None


# Workflow utils
def prompt_arg_parser(prompt: str, prompt_args: Optional[dict]) -> str:
    """Format the prompt with the provided arguments."""
    if prompt_args is not None:
        prompt = prompt.format(**prompt_args)
    return prompt


async def async_run_workflow(
    workflow: AgentWorkflow,
    prompt: str,
    prompt_args: Optional[dict] = None,
    verbose: bool = False,
) -> dict:
    r"""Async run workflow and return the final state."""

    prompt = prompt_arg_parser(prompt, prompt_args)
    if verbose:
        pprint(f"💬 User: {prompt}")

    handler = workflow.run(user_msg=prompt)

    if verbose:
        cur_agent = None
        async for event in handler.stream_events():
            if (
                hasattr(event, "current_agent_name")
                and event.current_agent_name != cur_agent
            ):
                cur_agent = event.current_agent_name
                print(f"\n{'='*50}")
                print(f"🤖 Agent: {cur_agent}")
                print(f"{'='*50}\n")
            elif isinstance(event, AgentOutput):
                if event.response.content:
                    print(f"📝 Output: {event.response.content}")
                if event.tool_calls:
                    print(
                        f"🔧 Planning to use tools:",
                        [tool_call.tool_name for tool_call in event.tool_calls]
                    )
            elif isinstance(event, ToolCallResult):
                print(f"🔧 Tool Result ({event.tool_name}):")
                print(f"  Arguments: {event.tool_kwargs}")
                print(f"  Output: {event.tool_output}")
            elif isinstance(event, ToolCall):
                print(f"🔨 Calling Tool: {event.tool_name}")
                print(f"  Arguments: {event.tool_kwargs}")

    final_state = await handler.ctx.get("state")
    return final_state
