"""
Pico LCD 1.3 driver implementation.

see: https://www.waveshare.com/wiki/Pico-LCD-1.3
"""
__all__ = ["PicoLCDDriver", "PicoLCDColorspace"]
import enum
import typing

import framebuf
from machine import Pin, PWM, SPI

from .colors import Color, RGB565
from .frame_buffer import FrameBuffer


class PicoLCDColorspace(enum.IntEnum):
    """Supported color spaces by the PicoLCD 1.3 driver"""

    # RGB444 = enum.auto()
    RGB565 = framebuf.RGB565
    # RGB666 = enum.auto()


class PicoLCDDriver:
    """
    Driver for Pico LCD 1.3

    Display size is 240x240 pixels
    Color spaces are RGB444, RGB565, RGB666
    However it appears that FrameBuffer only supports RGB565.

    :param color_space: Display color space, default is RGB565
    """
    # Dimensions
    __WIDTH = 240
    __HEIGHT = 240

    # Pin setup
    __DATA_COMMAND = 8  # Data/Command switch
    __CHIP_SELECT = 9  # Chip Select, Low Active
    __CLOCK = 10  # SPI Clock input
    __DATA = 11  # SPI Data Input
    __RESET = 12  # Reset pin, Low Active
    __BACKLIGHT = 13  # Screen backlight

    def __init__(self, color_space: PicoLCDColorspace = PicoLCDColorspace.RGB565):
        self._color_space = color_space

        # Setup pins
        self.__chip_select = Pin(self.__CHIP_SELECT, Pin.OUT)
        self.__reset = Pin(self.__RESET, Pin.OUT)
        self.__spi = SPI(
            1,
            100000000,
            polarity=0,
            phase=0,
            sck=Pin(self.__CLOCK),
            mosi=Pin(self.__DATA),
            miso=None,
        )
        self.__data_command = Pin(self.__DATA_COMMAND, Pin.OUT)
        self.__chip_select.value(1)
        self.__data_command.value(1)
        self.__brightness = PWM(Pin(self.__BACKLIGHT))
        self.__brightness_level = 0xFFFF

        self._init_display()

    # Implement LCDDriver Protocol
    @property
    def Color(self) -> typing.Type[Color]:  # noqa: N802
        """
        Driver color class alias.

        Using class naming conventions as this returns Color or a class derived from Color.

        :return: Driver Color class
        :rtype: class inheriting from Color
        """
        if self._color_space == PicoLCDColorspace.RGB565:
            return RGB565

        return Color

    @property
    def width(self) -> int:
        return self.__WIDTH

    @property
    def height(self) -> int:
        return self.__HEIGHT

    def make_frame_buffer(self) -> FrameBuffer:
        """
        Generates a new FrameBuffer for the application.

        The framebuffer is with display parameters.
        """
        return FrameBuffer(bytearray(self.height * self.width * 2), self.width, self.height, self._color_space)

    def show(self, buffer: FrameBuffer):
        """Displays the current FrameBuffer status on the LCD."""
        self._caset(0x0000, 0x00EF)
        self._raset(0x0000, 0x00EF)
        self._rawwr(buffer.buffer)

    def sleep(self):
        """Puts the LCD into sleep mode."""
        self.__brightness.duty_u16(0)
        self._dispoff()
        self._slpin()

    def wake(self):
        """Wakes up the LCD."""
        self._slpout()
        self._dispon()
        self.dim()

    def dim(self, brightness: typing.Optional[float] = None):
        """
        Sets LCD backlight to the specified brightness

        :param brightness: Brightness value between 0 and 1
        """
        if brightness is not None:
            if not 0 <= brightness <= 1:
                raise ValueError("brightness must be between 0 and 1.")

            self.__brightness_level = int(brightness * 0xFFFF)
        self.__brightness.duty_u16(self.__brightness_level)

    def _send_command(self, command: int, data: typing.Optional[bytearray] = None):
        """
        Sends a command to the LCD Controller

        :param command: Command to send, 1 byte
        :param data: Data stream attached to the command, list of bytes
        """
        if command & ~0xFF:
            raise ValueError("Commands are 1 byte.")

        # Set display in command mode
        self.__chip_select.value(1)
        self.__data_command.value(0)
        self.__chip_select.value(0)
        # Writes command
        self.__spi.write(bytearray([command]))
        # Ends command
        self.__chip_select.value(1)

        if not data:
            return

        # Set display in data mode
        self.__chip_select.value(1)
        self.__data_command.value(1)
        self.__chip_select.value(0)
        # Writes data
        self.__spi.write(data)
        # Ends data
        self.__chip_select.value(1)

    def _reset_display(self):
        """Resets the display"""
        self.__reset.value(1)
        self.__reset.value(0)
        self.__reset.value(1)

    def _init_display(self):
        """Initializes the display"""
        self._reset_display()

        self._madctl(0x70)  # B>T, L>R, Norm, LCD T>B, RGB, LCD L>R
        self._colmod(0x05)  # 65K of RGB interface
        self._porctrl(0x0C, 0x0C, 0, 0x03, 0x03, 0x03, 0x03)  # Default
        self._gctrl(0x03, 0x05)  # 13.26, -10.43
        self._vcoms(0x19)  # 0.725
        self._lcmctrl(0x2C)  # Default
        self._vdvvrhen(True)  # Read VRD/VRH from commands
        self._vrhs(0x12)  # +/- 4.45 + (vcom + vcom offeset + vdv)
        self._vdvs(0x20)  # 0
        self._frctrl2(False, 0xF)  # Dot Inversion at 60Hz
        self._pwctrl1(0x01, 0x01, 0x01)  # 6.6/-4.6/2.3
        self._pvgamctrl(  # Using values from manufacturer code example
            vp0=0x0,
            vp1=0x04,
            vp2=0x0D,
            vp4=0x11,
            vp6=0x13,
            vp13=0xB,
            vp20=0x3F,
            vp27=0x4,
            vp36=0x5,
            vp43=0x4C,
            vp50=0x8,
            vp57=0x0D,
            vp59=0x0B,
            vp61=0x1F,
            vp62=0x23,
            vp63=0xD,
            jp0=0x2,
            jp1=0x1,
        )
        self._nvgamctrl(  # Using values from manufacturer code example
            vp0=0x0,
            vp1=0x04,
            vp2=0x0D,
            vp4=0x11,
            vp6=0x13,
            vp13=0xB,
            vp20=0x3F,
            vp27=0x4,
            vp36=0x5,
            vp43=0x4C,
            vp50=0x8,
            vp57=0x0D,
            vp59=0x0B,
            vp61=0x1F,
            vp62=0x23,
            vp63=0xD,
            jp0=0x2,
            jp1=0x1,
        )
        self._invon()
        self._slpout()
        self._dispon()

    # Command list
    # See: https://www.waveshare.com/w/upload/a/ad/ST7789VW.pdf
    def _madctl(self, data: int):
        """
        Command MADCTL: Memory Access Control

        :param data: b[MY, MX, MV, RBG, 0, 0, 0]
        """
        if not 0 <= data <= 255:
            raise ValueError("MADCTL requires 1 byte.")

        self._send_command(0x36, bytearray([data]))

    def _colmod(self, data: int):
        """
        Command COLMOD: Interface pixel format
        :param data: b[0, D6, D5, D4, 0, D2, D1, D0]
        """
        if not 0 <= data <= 255:
            raise ValueError("COLMOD requires 1 byte.")

        self._send_command(0x3A, bytearray([data]))

    def _porctrl(self, bpa: int, fpa: int, psen: int, bpb: int, fpb: int, bpc: int, fpc: int, /):
        """
        PORCTRL: Porch Control

        Default:

        * Reset: 0x0C, 0x0C, 0, 0x03, 0x03, 0x03, 0x03
        * S/W Reset: 0x0C, 0x0C, 0, 0x03, 0x03, 0x03, 0x03
        * H/W Reset: 0x0C, 0x0C, 0, 0x03, 0x03, 0x03, 0x03

        :param bpa: Back porch in normal mode 0x01 to 0x7F
        :param fpa: Front porch in normal mode 0x1 to 0x7F
        :param psen: Enable separate porch control 0 or 1
        :param bpb: Back porch in idle mode 0x01 to 0X0F
        :param fpb: Front porch in idle mode 0x01 to 0x0F
        :param bpc: Back porch in partial mode 0x01 to 0x0F
        :param fpc: Front porch in partial mode 0x01 to 0x0F
        """
        if bpa & ~0x7F or not bpa:
            raise ValueError("PORCTRL bpa must be between 0x01 and 0x7F.")
        if fpa & ~0x7F or not fpa:
            raise ValueError("PORCTRL fpa must be between 0x01 and 0x7F.")
        if bpb & ~0x0F or not bpb:
            raise ValueError("PORCTRL bpb must be between 0x01 and 0x0F.")
        if fpb & ~0x0F or not fpb:
            raise ValueError("PORCTRL fpb must be between 0x01 and 0x0F.")
        if bpc & ~0x0F or not bpc:
            raise ValueError("PORCTRL bpc must be between 0x01 and 0x0F.")
        if fpc & ~0x0F or not fpc:
            raise ValueError("PORCTRL fpc must be between 0x01 and 0x0F.")
        if psen not in (0, 1):
            raise ValueError("PORTCTRL psen must be 0 or 1.")

        self._send_command(
            0xB2,
            bytearray([bpa, fpa, psen, bpb << 8 + fpb, bpc << 8 + fpc]),
        )

    def _gctrl(self, vghs: int, vgls: int, /):
        """
        GCTRL: Gate Control

        :param vghs: 3 bits
        :param vgls: 3 bits
        """
        if vghs & ~0x07:
            raise ValueError("GCTRL vghs must be between 0 and 0x07.")
        if vgls & ~0x07:
            raise ValueError("GCTRL vgls must be between 0 and 0x07.")

        self._send_command(0xB7, bytearray([vghs << 8 + vgls]))

    def _vcoms(self, setting: int):
        """
        VCOMS: VCOM Settings

        :param setting: 6 bits, default 0x00
        """
        if setting & ~0x3F:
            raise ValueError("VCOMS setting must be between 0x00 and 0x3F.")

        self._send_command(0xBB, bytearray([setting]))

    def _lcmctrl(self, parameter: int):
        """
        LCMCTRL: LCM Control

        :param parameter: b[0, XMY, XRGB, XINV, XMX, XMH, XGH] default is 0x2C
        """
        if parameter & ~0x7F:
            raise ValueError("LCMCTRL parameter must be between 0 and 0x7F.")

        self._send_command(0xC0, bytearray([parameter]))

    def _vdvvrhen(self, enable: bool):
        """
        VDVVRHEN: VDV and VRH enable

        enable defines the source as:

        * False: Value comes from NVM
        * True: Value comes from command write

        Default is True.

        :param enable: Defines source for VDV and VRH registers
        """
        self._send_command(0xC2, bytearray([int(enable), 0xFF]))

    def _vrhs(self, value: int):
        """
        VRHS: VRH Set

        :param value: VRH value, between 0x00 and 0x3F
        """
        if value & ~0x3F:
            raise ValueError("VRHS value must be between 0 and 0x3F.")
        self._send_command(0xC3, bytearray([value]))

    def _vdvs(self, value: int):
        """
        VDVS: VDV Set

        :param value: VDV value, between 0x00 and 0x3F
        """
        if value & ~0x3F:
            raise ValueError("VDVS value must be between 0 and 0x3F.")
        self._send_command(0xC4, bytearray([value]))

    def _frctrl2(self, nla: bool, rtna: int):
        """
        FRCTRL2: Framerate Control in normal mode

        :param nla: True is dot inversion, False is column inversion
        :param rtna: Frame rate setting, between 0x00 and 0x1F
        """
        if rtna & ~0x1F:
            raise ValueError("FRCTRL2 rtna must be between 0 and 0x1F.")

        # NLA is 3 bits all set to 1 or all set to 0
        # Parameter is b[NLA2, NLA1, NLA0, RTNA4, RTNA3, RTNA2, RTNA1, RTNA0]
        self._send_command(0xC6, bytearray([((nla and 0x07 or 0x00) << 5) + rtna]))

    def _pwctrl1(self, avdd: int, avcl: int, vds: int):
        """
        PWCTRL1: Power Control 1

        :param avdd: 2 bits value
        :param avcl: 2 bits value
        :param vds: 2 bits value
        """
        if avdd & ~0x03:
            raise ValueError("PWCTRL1 avdd must be between 0 and 3")
        if avcl & ~0x03:
            raise ValueError("PWCTRL1 avcl must be between 0 and 3")
        if vds & ~0x03:
            raise ValueError("PWCTRL1 vds must be between 0 and 3")
        self._send_command(0xD0, bytearray([
            0xA4,  # Constant
            (avdd << 6) + (avcl << 4) + vds,
        ]))

    def _pvgamctrl(
            self,
            vp0: int,
            vp1: int,
            vp2: int,
            vp4: int,
            vp6: int,
            vp13: int,
            vp20: int,
            vp27: int,
            vp36: int,
            vp43: int,
            vp50: int,
            vp57: int,
            vp59: int,
            vp61: int,
            vp62: int,
            vp63: int,
            jp0: int,
            jp1: int,
    ):
        """
        PVGAMCTRL: Positive Voltage Gamma Control

        :param vp0: 4 bits, default 0x0
        :param vp1: 6 bits, default 0x2C
        :param vp2: 6 bits, default 0x2E
        :param vp4: 5 bits, default 0x15
        :param vp6: 5 bits, default 0x10
        :param vp13: 4 bits, default 0x9
        :param vp20: 7 bits, default 0x48
        :param vp27: 3 bits, default 0x3
        :param vp36: 3 bits, default 0x3
        :param vp43: 7 bits, default 0x53
        :param vp50: 4 bits, default 0xB
        :param vp57: 5 bits, default 0x19
        :param vp59: 5 bits, default 0x18
        :param vp61: 6 bits, default 0x18
        :param vp62: 6 bits, default 0x25
        :param vp63: 4 bits, default 0x7
        :param jp0: 2 bits, default 0x0
        :param jp1: 2 bits, default 0x0
        """
        self.__gamma_voltage_ctrl(
            0xE0, vp0, vp1, vp2, vp4, vp6, vp13, vp20, vp27, vp36, vp43, vp50, vp57, vp59, vp61, vp62, vp63, jp0, jp1
        )

    def _nvgamctrl(
            self,
            vp0: int,
            vp1: int,
            vp2: int,
            vp4: int,
            vp6: int,
            vp13: int,
            vp20: int,
            vp27: int,
            vp36: int,
            vp43: int,
            vp50: int,
            vp57: int,
            vp59: int,
            vp61: int,
            vp62: int,
            vp63: int,
            jp0: int,
            jp1: int,
    ):
        """
        NVGAMCTRL: Negative Voltage Gamma Control

        :param vp0: 4 bits, default 0x0
        :param vp1: 6 bits, default 0x2C
        :param vp2: 6 bits, default 0x2E
        :param vp4: 5 bits, default 0x15
        :param vp6: 5 bits, default 0x10
        :param vp13: 4 bits, default 0x9
        :param vp20: 7 bits, default 0x48
        :param vp27: 3 bits, default 0x3
        :param vp36: 3 bits, default 0x3
        :param vp43: 7 bits, default 0x53
        :param vp50: 4 bits, default 0xB
        :param vp57: 5 bits, default 0x19
        :param vp59: 5 bits, default 0x18
        :param vp61: 6 bits, default 0x18
        :param vp62: 6 bits, default 0x25
        :param vp63: 4 bits, default 0x7
        :param jp0: 2 bits, default 0x0
        :param jp1: 2 bits, default 0x0
        """
        self.__gamma_voltage_ctrl(
            0xE1, vp0, vp1, vp2, vp4, vp6, vp13, vp20, vp27, vp36, vp43, vp50, vp57, vp59, vp61, vp62, vp63, jp0, jp1
        )

    def _invon(self):
        """
        INVON: Display Inversion ON

        This command is used to recover from display inversion mode
        """
        self._send_command(0x21)

    def _slpout(self):
        """
        SLPOUT: Sleep Out

        Turns off sleep mode
        """
        self._send_command(0x11)

    def _slpin(self):
        """
        SLPIN: Sleep In

        Turns on sleep mode
        """
        self._send_command(0x10)

    def _dispon(self):
        """
        DISPON: Display ON

        Turns on the display
        """
        self._send_command(0x29)

    def _dispoff(self):
        """
        DISPOFF: Display OFF

        Turns off the display
        """
        self._send_command(0x28)

    def _caset(self, xs: int, xe: int):
        """
        CASET: Column Address Set

        Out of range values are ignored

        If mv = 0 then 0 < xs < xe < 0x00EF
        If mv = 1 then 0 < xs < xe < 0x013F

        :param xs: 16 bits int
        :param xe: 16 bits int
        """
        if not 0 < xs < xe < 0x013F:
            raise ValueError("CASET parameters are invalid.")

        self._send_command(0x2A, bytearray([
            xs >> 8,
            xs & 0xFF,
            xe >> 8,
            xe & 0xFF,
        ]))

    def _raset(self, ys: int, ye: int):
        """
        RASET: Row Address Set

        Out of range values are ignored

        if mv = 0 then 0 < ys < ye < 0x013F
        if mv = 1 then 0 < ys < ye < 0x00EF
        :param ys: 16 bits int
        :param ye: 16 bits int
        """
        if not 0 < ys < ye < 0x013F:
            raise ValueError("RASET parameters are invalid.")

        self._send_command(0x2B, bytearray([
            ys >> 8,
            ys & 0xFF,
            ye >> 8,
            ye & 0xFF,
        ]))

    def _rawwr(self, buffer: bytearray):
        """
        RAWWR: Memory Write

        Transfer data to frame memory

        :param buffer: frame buffer
        """
        self._send_command(0x2C, buffer)

    def __gamma_voltage_ctrl(
            self,
            command: int,
            vp0: int,
            vp1: int,
            vp2: int,
            vp4: int,
            vp6: int,
            vp13: int,
            vp20: int,
            vp27: int,
            vp36: int,
            vp43: int,
            vp50: int,
            vp57: int,
            vp59: int,
            vp61: int,
            vp62: int,
            vp63: int,
            jp0: int,
            jp1: int,
    ):
        """
        PVGAMCTRL: Positive Voltage Gamma Control

        :param command: Command to pass.
        :param vp0: 4 bits, default 0x0
        :param vp1: 6 bits, default 0x2C
        :param vp2: 6 bits, default 0x2E
        :param vp4: 5 bits, default 0x15
        :param vp6: 5 bits, default 0x10
        :param vp13: 4 bits, default 0x9
        :param vp20: 7 bits, default 0x48
        :param vp27: 3 bits, default 0x3
        :param vp36: 3 bits, default 0x3
        :param vp43: 7 bits, default 0x53
        :param vp50: 4 bits, default 0xB
        :param vp57: 5 bits, default 0x19
        :param vp59: 5 bits, default 0x18
        :param vp61: 6 bits, default 0x18
        :param vp62: 6 bits, default 0x25
        :param vp63: 4 bits, default 0x7
        :param jp0: 2 bits, default 0x0
        :param jp1: 2 bits, default 0x0
        """
        if vp0 & ~0xF:
            raise ValueError("PVGAMCTRL vp0 is 4 bits.")
        if vp1 & ~0x3F:
            raise ValueError("PVGAMCTRL vp1 is 6 bits.")
        if vp2 & ~0x3F:
            raise ValueError("PVGAMCTRL vp2 is 6 bits.")
        if vp4 & ~0x1F:
            raise ValueError("PVGAMCTRL vp4 is 5 bits.")
        if vp6 & ~0x1F:
            raise ValueError("PVGAMCTRL vp6 is 5 bits.")
        if vp13 & ~0xF:
            raise ValueError("PVGAMCTRL vp13 is 4 bits.")
        if vp20 & ~0x7F:
            raise ValueError("PVGAMCTRL vp20 is 7 bits.")
        if vp27 & ~0x7:
            raise ValueError("PVGAMCTRL vp27 is 3 bits.")
        if vp36 & ~0x7:
            raise ValueError("PVGAMCTRL vp36 is 3 bits.")
        if vp43 & ~0x7F:
            raise ValueError("PVGAMCTRL vp43 is 7 bits.")
        if vp50 & ~0xF:
            raise ValueError("PVGAMCTRL vp50 is 4 bits.")
        if vp57 & ~0x1F:
            raise ValueError("PVGAMCTRL vp57 is 5 bits.")
        if vp59 & ~0x1F:
            raise ValueError("PVGAMCTRL vp59 is 5 bits.")
        if vp61 & ~0x3F:
            raise ValueError("PVGAMCTRL vp61 is 6 bits.")
        if vp62 & ~0x3F:
            raise ValueError("PVGAMCTRL vp62 is 6 bits.")
        if vp63 & ~0xF:
            raise ValueError("PVGAMCTRL vp63 is 4 bits.")
        if jp0 & ~0x3:
            raise ValueError("PVGAMCTRL jp0 is 2 bits.")
        if jp1 & ~0x3:
            raise ValueError("PVGAMCTRL jp1 is 2 bits.")

        self._send_command(command, bytearray([
            (vp63 << 4) + vp0,
            vp1,
            vp2,
            vp4,
            vp6,
            (jp0 << 4) + vp13,
            vp20,
            (vp36 << 4) + vp27,
            vp43,
            (jp1 << 4) + vp50,
            vp57,
            vp59,
            vp61,
            vp62,
        ]))
