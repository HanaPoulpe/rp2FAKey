"""
Defines the input pins used by the board.

Our system requires:

- a Joystick
- a Select button
- a Cancel button
- an Unlock Button

Supports:

- a Quick setting button
- a WiFi trigger button
- a Sleep button
"""
__all__ = ['KeyStatus', 'Pin', 'Controller', 'PRESSED', 'RELEASED']

import typing

from .types import KeyStatus


RELEASED, PRESSED = 1, 0


class Pin(typing.Protocol):
    """
    Generic input pin interface.

    More details: https://github.com/micropython/micropython/blob/master/docs/library/machine.Pin.rst
    """

    def value(self) -> int:
        """
        Pin value

        :returns: 0 if released, 1 is pressed
        """
        ...

    def irq(
            self,
            callback: typing.Callable[['Pin'], None],
            trigger: int = 0xFF,
            *,
            priority: int = 1,
            wake=None,
            hard: bool = False
    ):
        """
        Sets an IRQ Handler on the Pin.

        :param callback: Callback function
        :param trigger: Trigger type
        :param priority: IRQ Priority, higher is higher priority
        :param wake: Wake from power machine sleep modes
        :param hard: is hardware interrupt
        """
        ...


class Controller(typing.Protocol):
    """Standard controller."""

    @classmethod
    @property
    def KEY_PRESSED(cls) -> int:  # noqa
        return 0  # pragma: no cover

    @classmethod
    @property
    def KEY_RELEASED(cls) -> int: # noqa
        return 0  # pragma: no cover

    def joy_up(self) -> Pin:
        """Returns if the UP button is pressed."""
        ...

    def joy_down(self) -> Pin:
        """Returns if the DOWN button is pressed."""
        ...

    def joy_left(self) -> Pin:
        """Returns if the LEFT button is pressed."""
        ...

    def joy_right(self) -> Pin:
        """Returns if the RIGHT button is pressed."""
        ...

    def select_button(self) -> Pin:
        """Returns if the SELECT button is pressed."""
        ...

    def cancel_button(self) -> Pin:
        """Returns if the CANCEL button is pressed."""
        ...

    def unlock_button(self) -> Pin:
        """Returns if the UNLOCK button is pressed."""
        ...

    def sleep_button(self) -> Pin:
        """Returns if the sleep button is pressed."""
        ...

    def wifi_toggle_button(self) -> Pin:
        """Returns if the wifi toggle button is pressed."""
        ...

    def settings_button(self) -> Pin:
        """Returns if the settings button is pressed."""
        ...

    def get_frame(self) -> KeyStatus:
        """
        Returns the current status of each keys.

        When a button is pressed, the matching value is 1
        When a button is not pressed, the matching value is 0
        """
        ...
