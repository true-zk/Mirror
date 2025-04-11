import os
from pathlib import Path
from datetime import datetime
import dateparser
from typing import Optional, Tuple

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import Document
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter

from mirror.conf import PERSIST_DIR


class DiaryManager:
    def __init__(self):
        self.persist_dir = PERSIST_DIR
        self.storage_context = self._load_or_create_storage()
        self.index: VectorStoreIndex = self._load_or_create_index()

    def _load_or_create_storage(self) -> StorageContext:
        os.makedirs(self.persist_dir, exist_ok=True)
        return StorageContext.from_defaults(
            docstore=SimpleDocumentStore(),
            vector_store=SimpleVectorStore(),
            index_store=SimpleIndexStore(),
            persist_dir=self.persist_dir
        )

    def _load_or_create_index(self) -> VectorStoreIndex:
        # if Path(self.persist_dir).exists():
        #     return VectorStoreIndex.from_vector_store(
        #         self.storage_context.vector_store,
        #         storage_context=self.storage_context
        #     )
        # else:
        return VectorStoreIndex.from_documents([], storage_context=self.storage_context)

    def _create_doc(self, content: str, date: Optional[str] = None) -> Document:
        if not date:
            date = datetime.today().strftime("%Y-%m-%d")
        return Document(text=content, metadata={"date": date})

    # def _parse_date_range(self, date_query: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    #     if not date_query:
    #         return None, None
    #     now = datetime.now()
    #     parsed = dateparser.parse(date_query, settings={"RELATIVE_BASE": now})
    #     if not parsed:
    #         return None, None
    #     date_str = parsed.strftime("%Y-%m-%d")
    #     return date_str, date_str  # 当前只解析单一日期，后续可扩展范围

    def _create_date_filtered_retriever(self, start_date: Optional[str], end_date: Optional[str]):  # TODO
        after_filter = MetadataFilter(
            key="date",
            value=start_date,
            operator=">="
        )
        before_filter = MetadataFilter(
            key="date",
            value=end_date,
            operator="<="
        )
        date_range_filters = MetadataFilters(
            filters=[after_filter, before_filter],
            mode="and"
        )
        retriever_ = self.index.as_retriever(
            similarity_top_k=5,
            filters=date_range_filters
        )
        return retriever_

    # Interfaces
    def add_diary(self, content: str, date: Optional[str] = None):
        doc = self._create_doc(content, date)
        self.index.insert(doc)
        self.storage_context.persist()
    
    def query(self, question: str, date_query: Optional[str] = None):
        start_date, end_date = self._parse_date_range(date_query)  # TODO
        retriever = self._create_date_filtered_retriever(start_date, end_date)
        engine = RetrieverQueryEngine.from_args(retriever)
        return engine.query(question)
