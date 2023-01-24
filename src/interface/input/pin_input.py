"""
Defines a direct wired pin interface.

This allows easy mapping of button to the board pins.
"""
from machine import Pin

from .null_pin import NullPin
from .types import KeyStatus


class PinInput:
    """
    Wires board pins to the matching buttons directly.

    Value set to 0 means the button is not mapped.

    :param up: UP Button pin number
    :param down: DOWN Button pin number
    :param left: LEFT Button pin number
    :param right: RIGHT Button pin number
    :param select: SELECT Button pin number
    :param cancel: CANCEL Button pin number
    :param unlock: UNLOCK Button pin number
    :param settings: SETTINGS Button pin number, not mandatory
    :param wifi: WIFI Toggle Button pin number, not mandatory
    :param sleep: SLEEP Button pin number, not mandatory
    """

    KEY_PRESSED = 1
    KEY_RELEASED = 0

    def __init__(self, up, down, left, right, select, cancel, unlock, settings=0, wifi=0, sleep=0):
        def _check(lst: list[int], key: int) -> list[int]:
            if key in lst:
                raise ValueError("Multiple buttons are mapped to the same pin.")
            lst.append(key)
            return lst

        def _make_pin(lst: list[int], pin: int) -> tuple[Pin, list[int]]:
            if pin == 0:
                return NullPin

            return Pin(pin, Pin.OUT, Pin.PULL_UP), _check(lst, pin)

        if 0 in (up, down, left, right, select, cancel, unlock):
            raise ValueError("All up, down, left, right, select, cancel and unlock are mandatory.")

        self._up, check = _make_pin([], up)
        self._down, check = _make_pin(check, down)
        self._left, check = _make_pin(check, left)
        self._right, check = _make_pin(check, right)
        self._select, check = _make_pin(check, select)
        self._cancel, check = _make_pin(check, cancel)
        self._unlock, check = _make_pin(check, unlock)
        self._settings, check = _make_pin(check, settings)
        self._wifi, check = _make_pin(check, wifi)
        self._sleep, check = _make_pin(check, sleep)

    def joy_up(self) -> Pin:
        return self._up

    def joy_down(self) -> Pin:
        return self._down

    def joy_left(self) -> Pin:
        return self._left

    def joy_right(self) -> Pin:
        return self._right

    def select_button(self) -> Pin:
        return self._select

    def cancel_button(self) -> Pin:
        return self._cancel

    def unlock_button(self) -> Pin:
        return self._unlock

    def sleep_button(self) -> Pin:
        return self._sleep

    def settings_button(self) -> Pin:
        return self._settings

    def wifi_toggle_button(self) -> Pin:
        return self._wifi

    def get_frame(self) -> KeyStatus:
        return KeyStatus(
            up=self.joy_up().value() ^ 1,
            down=self.joy_down().value() ^ 1,
            left=self.joy_left().value() ^ 1,
            right=self.joy_right().value() ^ 1,
            select=self.select_button().value() ^ 1,
            cancel=self.cancel_button().value() ^ 1,
            unlock=self.unlock_button().value() ^ 1,
            sleep=self.sleep_button().value() ^ 1,
            settings=self.settings_button().value() ^ 1,
            wifi=self.wifi_toggle_button().value() ^ 1,
        )
