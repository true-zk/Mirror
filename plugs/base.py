from abc import ABC, abstractmethod


class BasePlugin(ABC):
    @property
    def name(self) -> str:
        """插件的名称"""
        pass

    @property
    def description(self) -> str:
        """插件的描述"""
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """所有的插件都需要实现这个方法，返回一个字符串，
        获取可以给LLM理解的今日数据"""
        pass
