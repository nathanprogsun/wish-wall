from typing import Any, Self, cast


class Singleton:
    _instance: Any | None = None
    _initialized = False

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not self._initialized:
            self._initialized = True
            super().__init__(*args, **kwargs)

    @classmethod
    def get_singleton_instance(cls) -> Self:
        if cls._instance is None:
            instance = cls()
            cls._instance = instance
        return cast("Self", cls._instance)

    @classmethod
    def has_instance(cls) -> bool:
        return cls._instance is not None
