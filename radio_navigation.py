import serial
import time
from dwm1001 import ActiveTag

RECTANGLE_SEGMENTS = [2, 4]  # 2 segments pour le rectangle que le robot va parcourir (2mx4m)

class RadioNavigation:
    def __init__(self, port):
        self.port = port
        self.connection = self.connect_to_device(port)
        self.initial_position = self.get_position()
        self.pos_x = 0
        self.pos_y = 0
        self.distance_x = 0
        self.distance_y = 0

    def connect_to_device(self, port):
        try:
            serial_handle = serial.Serial(port, baudrate=115200, timeout=1)
            time.sleep(1)
            print("Serial connection opened.")
            return serial_handle
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return None

    def get_position(self):
        if self.connection and self.connection.is_open:
            try:
                tag = ActiveTag(self.connection)
                tag.start_position_reporting()
                time.sleep(1)  # Add delay to allow the device to respond
                position = tag.position
                print(f"Received position: {position}")
                return {
                    'x': position.x_m,
                    'y': position.y_m,
                    'z': position.z_m,
                    'success_percentage': position.quality
                }
            except Exception as e:
                print(f"Error reading position: {e}")
        else:
            print("Serial connection is not open.")
        return None

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Serial connection closed.")