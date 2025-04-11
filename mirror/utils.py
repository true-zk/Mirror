from typing import Optional
import os
from pprint import pprint
from pathlib import Path
import requests
from datetime import datetime
from functools import partial
from colorama import Fore, Style

from llama_index.core.agent.workflow import (
    AgentWorkflow,
    AgentOutput,
    ToolCallResult,
    ToolCall
    )
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, SimpleDirectoryReader
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.schema import Document
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter
from llama_index.core.query_engine import RetrieverQueryEngine

from mirror.conf import PERSIST_DIR, DIARY_DIR
from mirror.models import bge_embedding_model, openai_like_llm


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


def iso_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").isoformat()


# Save Load and Index utils
def save_diary(diary: str, file_name: str) -> None:
    r"""Save the diary to the local file."""
    if not file_name.endswith(".md"):
        file_name += ".md"
    with open(os.path.join(DIARY_DIR, file_name), "w") as f:
        f.write(diary + "\n\n")


def get_index(force_load: bool = False) -> VectorStoreIndex:
    r"""Return the diary index.
    If set `force_load` to True, it will build the index from the diary doc.
    """
    index_path = Path(PERSIST_DIR)
    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore.from_persist_dir(PERSIST_DIR),
        vector_store=SimpleVectorStore.from_persist_dir(PERSIST_DIR),
        persist_dir=PERSIST_DIR
    )
    if index_path.exists() and not force_load:
        index = VectorStoreIndex.from_vector_store(
                vector_store=storage_context.vector_store,
                embed_model=bge_embedding_model()
            )
        return index
    else:
        storage_context.persist(persist_dir=PERSIST_DIR)
        index = VectorStoreIndex([], embed_model=bge_embedding_model())
        return index


def insert_diary_to_index(index: VectorStoreIndex, diary_doc: Document) -> None:
    r"""Insert the diary Document to the index."""
    index.insert(diary_doc)
    index.storage_context.persist(persist_dir=PERSIST_DIR)


def query_by_time(start: datetime, end: datetime) -> VectorIndexRetriever:
    r"""Query the diary index by time."""
    filters = MetadataFilters(
        filters=[
            MetadataFilter(
                key="date", 
                value=start.isoformat(),
                operator=">="
            ),
            MetadataFilter(
                key="date", 
                value=end.isoformat(),
                operator="<="
            )
        ]
    )
    return get_index().as_retriever(filters=filters)


def query_by_content(query: str, top_k: int = 5):
    r"""Query the diary index by content."""
    return get_index().as_retriever(similarity_top_k=top_k)


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
