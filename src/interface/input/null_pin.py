"""
Null pin definition

Using this class allows to never return None cleaning the downstream code.
"""
import typing


class _NullPin:
    """NullPin is never pressed."""

    @staticmethod
    def value() -> int:
        return 1

    @staticmethod
    def irq(
            callback: typing.Callable[['_NullPin'], None],
            trigger: int = 0xFF,
            *,
            priority: int = 1,
            wake=None,
            hard: bool = False
    ):
        """Do Nothing."""
        pass


NullPin = _NullPin()
