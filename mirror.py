from typing import List, Dict, Optional
from pathlib import Path
from functools import partial

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.llms import ChatMessage, LLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader, StorageContext, load_index_from_storage, Document
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import CustomQueryEngine, BaseQueryEngine

from plugs import BasePlugin


class Mirror:
    _base_prompt = (
        "你是一个叫{name}的用户私有日记系统。\n"
        "核心功能：\n"
        "1. 使用tools获取用户今日数据，根据数据生成日志\n"
        "2. 存储用户日志（自动记录时间戳）\n"
        "3. 通过检索历史日志进行总结\n"
        "4. 支持日志修改\n"
        "5. 和用户进行对话，当对话内容涉及用户历史信息时检索历史日志进行分析和回答\n\n"
        "操作指南：\n"
        "- 当用户说'保存日志'时，使用save_log_tool存储当前日志\n"
        "- 使用search_logs_tool时需包含时间范围参数\n"
        "- 生成总结时必须基于search_logs_tool的返回结果\n\n"
        "可用工具：\n{tool_descriptions}"
    )
    def __init__(
        self,
        name: str,
        plugins: List[BasePlugin],
        llm: Optional[LLM] = None,
        embedding_model: Optional[HuggingFaceEmbedding] = None,
        storage_path: str = "./mirror_storage",
    ):
        self.name = name
        self.plugins = plugins
        self._base_prompt = ChatMessage(
            role="system",
            content=self._base_prompt.format(name)
        )

        # init llm and embedding model
        if llm is not None:
            Settings.llm = llm
        self.llm = Settings.llm

        if embedding_model is not None:
            Settings.embed_model = embedding_model
        self.embedding_model = Settings.embed_model

        # init storage
        self.storage_path = Path(storage_path)
        self.log_index = self._setup_log_index()

    def _setup_log_index(self) -> VectorStoreIndex:
        r"""Load or create the log index."""
        if self.storage_path.exists():
            # Load existing index
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.storage_path / "index"),
            )
            return load_index_from_storage(storage_context)
        else:
            # Create new index
            return VectorStoreIndex(
                embed_model=self.embedding_model,
                storage_context=StorageContext.from_defaults(
                    persist_dir=str(self.storage_path / "index"),
                )
            )

    def _create_tools(self) -> None:
        """创建tools"""
        # 1. 插件工具 用于获取今日数据
        self.tools = []
        for plugin in self.plugins:
            self.tools.append(plugin.get_tool())
        
        # 2. 日志生成工具

        # 3. 日志存储工具

        # 4. 日志检索工具

        # 5. 日志修改工具


    def _insert_index(self, log: str, metadata: Dict) -> None:
        """插入日志到索引"""
        self.log_index.insert(
            Document(
                text=log,
                metadata=metadata
            )
        )
    
    def generate_log(self, data: str) -> str:
        """
        使用 llm 根据传入数据生成日志内容。
        输入参数：
            data: 今日数据（由其它插件获取的数据）
        返回：
            生成的日志文本
        """
        prompt = f"请根据以下数据生成今日日志：\n{data}\n日志内容："
        log = self.llm.call(prompt)
        return log
