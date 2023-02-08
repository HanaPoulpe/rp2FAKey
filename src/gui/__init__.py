"""
Manage GUI display.
"""
import enum
import typing
from typing import Union

from interface import Controller, FrameBuffer, Color, KeyStatus


class ReturnCode(enum.IntEnum):
    """Supports return codes"""
    OK = enum.auto()
    ERROR = enum.auto()
    CANCEL = enum.auto()


class ApplicationReturn:
    """
    Application return values

    :param code: returned code
    :param value: returned value
    """

    def __init__(self, code: ReturnCode, value: typing.Optional[typing.Any]):
        self.code = code
        self.value = value


class Application(typing.Protocol):
    """
    Defines a Graphical Application
    """

    def run(
            self, *,
            inputs: Controller,
            frame_buffer_factory: typing.Callable[[], FrameBuffer],
            display: typing.Callable[[FrameBuffer], None],
            color_class: typing.Type[Color],
            **kwargs
    ) -> ApplicationReturn:
        """
        Application main function

        :param inputs: Input controller to use
        :param frame_buffer_factory: Function that provides frame buffers
        :param display: Function that displays the framebuffer
        :param color_class: class that handles colorspace
        :param kwargs: Other parameters
        :returns: A return code
        """
        ...

    def wake(self):
        """Wakes the application."""
        ...

    def sleep(self):
        """Puts the application in sleep mode."""
        ...
