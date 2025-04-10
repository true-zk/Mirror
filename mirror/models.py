import os

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.llms.openai_like import OpenAILike

from mirror.conf import DASHSCOPE_KEY, CACHE_DIR, EMBED_MODEL_DIR


# llms
def dash_scope_qwen(**kwargs):
    dashscope_llm = DashScope(
        model_name=DashScopeGenerationModels.QWEN_MAX,
        api_key=DASHSCOPE_KEY
        )
    return dashscope_llm


def openai_like_llm(**kwargs):
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


# embedding models
def bge_embedding_model(**kwargs) -> HuggingFaceEmbedding:
    embed_model = HuggingFaceEmbedding(
        model_name=os.path.join(EMBED_MODEL_DIR),
        cache_folder=CACHE_DIR,
        **kwargs,
    )
    return embed_model


# test functions
def test_bge_embedding_model():
    from llama_index.core import VectorStoreIndex, Document
    documents = [Document(text="量子计算利用量子比特实现并行计算")]
    embed_model = bge_embedding_model()
    index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model
    )
    query_engine = index.as_query_engine(llm=dash_scope_qwen())
    response = query_engine.query("量子比特的作用是什么？")
    print(response)


def test_dash_scope_qwen():
    llm = dash_scope_qwen()
    resp = llm.complete("How to make cake?")
    print(resp)