from pathlib import Path
import sys
from typing import NoReturn
from serial import Serial
import dwm1001


def main() -> NoReturn:
    serial_handle = Serial("/dev/ttyACM0", baudrate=115_200)
    tag = dwm1001.ActiveTag(serial_handle)
    tag.start_position_reporting()

    while True:
        print("Position:")
        print(tag.position)


if __name__ == "__main__":
    main()