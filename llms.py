from conf import DASHSCOPE_KEY
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.llms.openai_like import OpenAILike


def dash_scope_qwen(**kwargs):
    dashscope_llm = DashScope(
        model_name=DashScopeGenerationModels.QWEN_MAX,
        api_key=DASHSCOPE_KEY
        )
    return dashscope_llm


def test_dash_scope_qwen():
    llm = dash_scope_qwen()
    resp = llm.complete("How to make cake?")
    print(resp)


def openai_like(**kwargs):
    """OpenAI-like LLM wrapper."""
    openai_llm = OpenAILike(
        model="qwen-max",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        is_chat_model=True,
        is_function_calling_model=True,
        api_key=DASHSCOPE_KEY,
        **kwargs
    )
    return openai_llm