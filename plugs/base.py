from abc import ABC, abstractmethod

from llama_index.core.tools import FunctionTool


class BasePlugin(ABC):
    @abstractmethod
    def get_tool(self) -> FunctionTool:
        """所有的插件都需要实现这个方法，返回一个FunctionTool对象"""
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """所有的插件都需要实现这个方法，返回一个字符串，
        获取可以给LLM理解的今日数据"""
        pass
