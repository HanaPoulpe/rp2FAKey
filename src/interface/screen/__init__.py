"""
LCD Driver definition.

This extends the FrameBuffer by adding methods to:
* Draw the frame
* Put display in sleep mode
* Wake the display
* Handle the colorspace conversion for 24bits RGB color to the LCD color space
"""
__all__ = ["Color", "FrameBuffer", "LCDDriver"]
import typing

from .colors import Color
from .frame_buffer import FrameBuffer


class LCDDriver(typing.Protocol):
    """
    Generic LCD driver.

    This relies on framebuf.FrameBuffer and the color space conversion for Color Tuple
    """
    @property
    def Color(self) -> typing.Type[Color]:  # noqa: N802
        """
        Driver color class alias.

        Using class naming conventions as this returns Color or a class derived from Color.

        :return: Driver Color class
        :rtype: class inheriting from Color
        """
        return Color

    @property
    def length(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__}.length is not implemented.")

    @property
    def width(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__}.width is not implemented.")

    def make_frame_buffer(self) -> FrameBuffer:
        """
        Generates a new FrameBuffer for the application.

        The framebuffer is with display parameters.
        """
        ...

    def show(self, buffer: FrameBuffer):
        """
        Displays the current FrameBuffer status on the LCD.

        :param buffer: FrameBuffer to display
        """
        ...

    def sleep(self):
        """Puts the LCD into sleep mode."""
        ...

    def wake(self):
        """Wakes up the LCD."""
        ...

    def dim(self, brightness: float):
        """
        Sets LCD brightness

        :param brightness: brightness value between 0 and 1
        """
        ...
