import os
from typing import Optional
from datetime import datetime
from pathlib import Path

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import Document

from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


persist_dir = "./diary_storage"
# embed_model = HuggingFaceEmbedding(
#     model_name="",
#     cache_folder="",
# )


def load_or_create_storage() -> StorageContext:
    os.makedirs(persist_dir, exist_ok=True)
    return StorageContext.from_defaults(
        docstore=SimpleDocumentStore(),
        vector_store=SimpleVectorStore(),
        index_store=SimpleIndexStore(),
        persist_dir=persist_dir
    )


def load_or_create_index(storage_context: StorageContext) -> VectorStoreIndex:
    # if Path(persist_dir).exists():
    #     return VectorStoreIndex.from_vector_store(
    #         vector_store=storage_context.vector_store,
    #         storage_context=storage_context
    #         # embed_model=
    #     )
    # else:
    return VectorStoreIndex.from_documents([], storage_context=storage_context)


store_context = load_or_create_storage()
index = load_or_create_index(store_context)


# def _create_doc(content: str, date: Optional[str] = None) -> Document:
#     if not date:
#         date = datetime.today().strftime("%Y-%m-%d")
#     return Document(text=content, metadata={"date": date})


# def add_entry(content: str, date: Optional[str] = None):
#     doc = _create_doc(content, date)
#     index.insert_documents([doc])
#     self.storage_context.persist()


# diary.add_entry("今天一整天都在调试 CUDA 的 kernel，终于把 segment_sum 的实现跑通了！虽然累，但成就感爆棚。", "2025-04-09")
# diary.add_entry("下午去了咖啡馆，听着雨声写了一点论文，思路意外地清晰了许多。或许换个环境真的有用。", "2025-04-10")
# diary.add_entry("有点焦虑，感觉最近进度不太理想，尤其是模型训练总是过拟合。明天得好好整理一下思路。", "2025-04-11")
