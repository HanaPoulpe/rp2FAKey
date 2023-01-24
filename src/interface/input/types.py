"""Common type aliases for the library."""
import collections

KeyStatus = collections.namedtuple(
    "KeyStatus",  # KeyStatus stores status of each key for each input frame
    ('up', 'down', 'left', 'right', 'select', 'cancel', 'unlock', 'settings', 'wifi', 'sleep'),
)
