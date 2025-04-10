from typing import Optional
from pprint import pprint
from pathlib import Path
import requests
from datetime import datetime

from llama_index.core.agent.workflow import (
    AgentWorkflow,
    AgentOutput,
    ToolCallResult,
    ToolCall
    )
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core import VectorStoreIndex, StorageContext, SimpleVectorStore
# https://docs.llamaindex.ai/en/stable/community/integrations/vector_stores/#using-a-vector-store-as-an-index
from mirror.conf import PERSIST_DIR


# Basic utils
def get_date_location_weather() -> dict:
    # Today
    today = datetime.now().strftime("%Y年-%m月-%d日")

    # Location from IP address
    ip_response = requests.get('https://ipinfo.io/json')
    location_data = ip_response.json()
    city = location_data.get('city', 'Unknown')
    country = location_data.get('country', 'Unknown')

    # OpenWeatherMap API
    # TODO: Hard code here
    WEATHER_API_KEY = "29e7696c3b1a8c6de55d8ecc2685ae31"
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    weather_data = str(requests.get(weather_url).json())

    description = weather_data["weather"][0]["description"]
    temp = str(round(weather_data["main"]["temp"] - 273.15, 1)) + "°C"

    return {
        "date": today,
        "location": f"{city}, {country}",
        "weather": f"天气为 {description}，温度为 {temp}",
    }


# Store utils
def get_vec_store():
    store_path = Path(PERSIST_DIR)
    if not store_path.exists():
        store_path.mkdir(parents=True, exist_ok=True)
    storage_context = StorageContext.from_defaults(persist_dir=str(store_path))


# Workflow utils
def prompt_arg_parser(prompt: str, prompt_args: Optional[dict]) -> str:
    """Format the prompt with the provided arguments."""
    if prompt_args is not None:
        prompt = prompt.format(**prompt_args)
    return prompt


async def cmdoutput_agent_workflow1(
    workflow: AgentWorkflow,
    prompt: str,
    prompt_args: Optional[dict] = None,
):
    r"""Cmd print output for agent workflow with details."""

    print("🙁 Warning: cmd output run does not save any data.")
    print("🧪 This should only be used for testing.")

    prompt = prompt_arg_parser(prompt, prompt_args)
    pprint(f"💬 User: {prompt}")

    handler = workflow.run(user_msg=prompt)

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
