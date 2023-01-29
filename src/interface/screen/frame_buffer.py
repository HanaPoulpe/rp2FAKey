"""Extends framebuf.FrameBuffer to store the buffer in the frame buffer."""
import typing

import framebuf


class FrameBuffer(framebuf.FrameBuffer):
    """
    FrameBuffer object.

    One must specify valid *buffer*, *width*, *height*, *format* and
    optionally *stride*.  Invalid *buffer* size or dimensions may lead to
    unexpected errors.

    :param buffer: an object with a buffer protocol which must be large
        enough to contain every pixel defined by the width, height and
        format of the FrameBuffer.
    :param width: the width of the FrameBuffer in pixels
    :param height: the height of the FrameBuffer in pixels
    :param format: specifies the type of pixel used in the FrameBuffer;
        permissible values are listed under Constants below. These set the
        number of bits used to encode a color value and the layout of these
        bits in *buffer*.
        Where a color value c is passed to a method, c is a small integer
        with an encoding that is dependent on the format of the FrameBuffer.
    :param stride: is the number of pixels between each horizontal line
        of pixels in the FrameBuffer. This defaults to *width* but may
        need adjustments when implementing a FrameBuffer within another
        larger FrameBuffer or screen. The *buffer* size must accommodate
        an increased step size.
    """
    def __init__(self, buffer: bytearray, width: int, height: int, format: int, stride: typing.Optional[int] = None, /):
        super().__init__(buffer, width, height, format, stride or width)
        self.buffer = buffer
