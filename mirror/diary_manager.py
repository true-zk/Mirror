import os
from datetime import datetime
from typing import Optional, Tuple, List

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import Document
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter

from mirror.types import SingletonMeta
from mirror.conf import PERSIST_DIR, DIARY_DIR
from mirror.utils import (
    extract_date_range_from_prompt,
    success_print,
    warning_print,
)


class DiaryManager(metaclass=SingletonMeta):
    _instance = None
    def __init__(
        self,
        diary_dir: str = DIARY_DIR,
        persist_dir: str = PERSIST_DIR
    ):
        self.diary_dir = diary_dir
        self.persist_dir = persist_dir
        self.storage_context = self._load_or_create_storage()
        self.index: VectorStoreIndex = self._load_or_create_index()
        if not os.path.exists(self.diary_dir):
            os.makedirs(self.diary_dir, exist_ok=True)
        success_print(
            "📖 日记管理器已初始化，日记存储在：" + self.diary_dir + " "
            "索引存储在：" + self.persist_dir
        )
        self._instance = self
        success_print("📖 日记管理器单例已创建。")

    def _load_or_create_storage(self) -> StorageContext:
        os.makedirs(self.persist_dir, exist_ok=True)
        return StorageContext.from_defaults(
            docstore=SimpleDocumentStore(),
            vector_store=SimpleVectorStore(),
            index_store=SimpleIndexStore(),
            persist_dir=self.persist_dir
        )

    def _load_or_create_index(self) -> VectorStoreIndex:
        return VectorStoreIndex.from_documents([], storage_context=self.storage_context)

    def _date_to_timestamp(self, date: str) -> int:
        dt = datetime.strptime(date, "%Y-%m-%d")
        timestamp = int(dt.timestamp())
        return timestamp

    def _create_doc(self, content: str, date: Optional[str] = None) -> Document:
        content = f"\n\n日记：【日期：{date}----日记内容：" + content.strip() + "】"
        timestamp = self._date_to_timestamp(date)
        return Document(text=content, metadata={"date": date, "timestamp": timestamp})

    # Interfaces
    @classmethod
    def get_instance(cls) -> "DiaryManager":
        r"""Get the singleton instance of DiaryManager."""
        if cls._instance is None:
            msg = "DiaryManager is not initialized, init now."
            warning_print(msg)
            cls._instance = cls()
        return cls._instance

    def add_diary(self, content: str, date: Optional[str] = None):
        """添加日记"""
        if not date:
            date = datetime.today().strftime("%Y-%m-%d")
        # save diary
        with open(os.path.join(self.diary_dir, date + ".md"), "w+") as f:
            f.write(content + "\n\n")
        # save to index
        doc = self._create_doc(content, date)
        self.index.insert(doc)
        self.storage_context.persist()

    def get_weekly_diary(self) -> Tuple[List[str], int]:
        """获取本周的日记"""
        start_time, end_time = extract_date_range_from_prompt("本周")
        start_timestamp = self._date_to_timestamp(start_time)
        end_timestamp = self._date_to_timestamp(end_time)
        diary_list = os.listdir(self.diary_dir)
        weekly_diary = []
        for diary in diary_list:
            diary_date = diary.split(".")[0]
            if start_timestamp <= self._date_to_timestamp(diary_date) <= end_timestamp:
                with open(os.path.join(self.diary_dir, diary), "r") as f:
                    content = f.read()
                weekly_diary.append(content)
        if len(weekly_diary) == 0:
            return (["本周没有日记记录。"], 0)
        return (weekly_diary, len(weekly_diary))

    def query(self, question: str):
        start_date, end_date = extract_date_range_from_prompt(question)

        if start_date is None and end_date is None:
            question += "今天是" + datetime.today().strftime("%Y-%m-%d") + "，请根据日期范围回答我的问题。"
            engine = self.index.as_query_engine()
            return engine.query(question).response

        if start_date is None:
            start_date = datetime(1601, 1, 1)
        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")
        start_timestamp = self._date_to_timestamp(start_date)
        end_timestamp = self._date_to_timestamp(end_date)
        filters = MetadataFilters(
            filters=[
                MetadataFilter(key="timestamp", value=start_timestamp, operator=">="),
                MetadataFilter(key="timestamp", value=end_timestamp, operator="<="),
            ],
            condition="and"
        )
        sub_engine = self.index.as_query_engine(
            filters=filters,
            similarity_top_k=100,
        )
        return sub_engine.query(question).response
