from abc import ABCMeta
from enum import Enum


class SingletonMeta(type):
    """Singleton metaclass to ensure only one instance of a class exists."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonABCMeta(SingletonMeta, ABCMeta):
    pass


class VerboseLevel(Enum):
    """Verbose level for logging and debugging."""

    LOW = 1
    HIGH = 2
