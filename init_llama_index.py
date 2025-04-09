import os

from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage.storage_context import StorageContext

from conf import *
from llms import dash_scope_qwen
from embedding_model import bge_embedding_model


def init_llm_embed_model():
    Settings.llm = dash_scope_qwen()
    Settings.embed_model = bge_embedding_model()


def init_vec_store():
    if not os.path.exists(PERSIST_DIR):
        os.makedirs(PERSIST_DIR)

    documents = SimpleDirectoryReader(LOG_DIR).load_data()

    index = VectorStoreIndex.from_documents(
        documents,
        # storage_context=StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    )
    index.storage_context.persist()
    return index


def init_all():
    init_llm_embed_model()
    index = init_vec_store()
    query_engine = index.as_query_engine(
        similarity_top_k=3,
        response_mode="compact",
        use_async=True,
    )
    return index, query_engine