import os

from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from mirror.conf import DASHSCOPE_KEY, CACHE_DIR, EMBED_MODEL_DIR


# llms
# def openai_like_llm(**kwargs):
#     """Return the openai like llm."""
#     openai_llm = OpenAILike(
#         model="qwen-max",
#         api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
#         is_chat_model=True,
#         is_function_calling_model=True,
#         api_key=DASHSCOPE_KEY,
#         **kwargs
#     )
#     return openai_llm


from mirror.conf import LOCAL_LLM_KEY, LOCAL_LLM_URL
def openai_like_llm(**kwargs):
    """Return the openai like llm."""
    openai_llm = OpenAILike(
        model="deepseek-chat",
        api_base=LOCAL_LLM_URL,
        is_chat_model=True,
        is_function_calling_model=True,
        api_key=LOCAL_LLM_KEY,
        **kwargs
    )
    return openai_llm


# embedding models
def bge_embedding_model(**kwargs) -> HuggingFaceEmbedding:
    r"""Return the local bge embedding model."""
    embed_model = HuggingFaceEmbedding(
        model_name=os.path.join(EMBED_MODEL_DIR),
        cache_folder=CACHE_DIR,
        **kwargs,
    )
    return embed_model
