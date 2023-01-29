"""Handles color spaces."""


class Color:
    """Manages the 24bit RGB"""

    def __init__(self, red: int, green: int, blue: int):
        if not 0 <= red <= 255:
            raise ValueError("red must be a 1 byte integer.")
        if not 0 <= green <= 255:
            raise ValueError("green must be a 1 byte integer.")
        if not 0 <= blue <= 255:
            raise ValueError("blue must be a 1 byte integer.")

        self.red = red
        self.green = green
        self.blue = blue

    def to_int(self) -> int:
        """Converts the color to integer."""
        return self.red + (self.green << 8) + (self.blue << 16)


class RGB565(Color):
    """Manages RGB565 color space."""
    def to_int(self) -> int:
        return (
            ((self.red & 0b11111000) << 8) +  # Keep 5 most significant bits from R and shift 8 bits
            ((self.green & 0b11111100) << 3) +  # Keep 6 most significant bits from G and shift 3 bits
            (self.blue >> 3)  # Keep 5 most significant bits and align them to the right
        )
