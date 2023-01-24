"""
Maps input to the Pico LCD1.3 pinout

see: https://www.waveshare.com/wiki/Pico-LCD-1.3
"""
import collections

from .pin_input import PinInput


KEY_A = 15
KEY_B = 17
KEY_X = 19
KEY_Y = 21
KEY_CTRL = 3
JOY_UP = 2
JOY_DOWN = 18
JOY_LEFT = 16
JOY_RIGHT = 20


KeyMapping = collections.namedtuple(
    "KeyMapping",
    ('up', 'down', 'left', 'right', 'select', 'cancel', 'unlock', 'settings', 'wifi', 'sleep'),
)

DEFAULT_MAPPING = KeyMapping(JOY_UP, JOY_DOWN, JOY_LEFT, JOY_RIGHT, KEY_CTRL, KEY_Y, KEY_X, KEY_A, KEY_B, 0)


class PicoLCDInputs(PinInput):
    """
    Input pins for Pico LCD1.3

    :param mapping: Key mapping to use.
    """

    def __init__(self, mapping: KeyMapping):
        super().__init__(*mapping)
