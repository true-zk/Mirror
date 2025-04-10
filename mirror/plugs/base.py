from abc import ABCMeta, abstractmethod

from llama_index.core.tools import FunctionTool


class SingletonMeta(type):
    """Singleton metaclass to ensure only one instance of a class exists."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonABCMeta(SingletonMeta, ABCMeta):
    pass


class BasePlugin(metaclass=SingletonABCMeta):
    @abstractmethod
    def get_tool(self) -> FunctionTool:
        """所有的插件都需要实现这个方法，返回一个FunctionTool对象"""
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """所有的插件都需要实现这个方法，返回一个字符串，
        获取可以给LLM理解的今日数据"""
        pass
