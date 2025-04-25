from abc import ABC, abstractmethod


class BaseQueue(ABC):

    @abstractmethod
    def get_base_key(self, *args, **kwargs) -> str: ...

    @abstractmethod
    def get_queue_key(self, *args, **kwargs) -> str: ...

    @abstractmethod
    def get_lock_key(self, *args, **kwargs) -> str: ...

    @abstractmethod
    def add_item(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def is_empty(self, *args, **kwargs) -> bool: ...

    @abstractmethod
    def pop_all(self, *args, **kwargs) -> list: ...

    @abstractmethod
    def clear_queue(self, *args, **kwargs) -> None: ...
