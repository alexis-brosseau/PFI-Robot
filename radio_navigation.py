from threading import Thread
import serial
import time
import math

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
            ser = serial.Serial()
            ser.port = port
            ser.baudrate = 115200
            ser.bytesize = serial.EIGHTBITS
            ser.parity = serial.PARITY_NONE
            ser.stopbits = serial.STOPBITS_ONE
            ser.timeout = 1
            ser.open()
            ser.write(b'\r\r')
            time.sleep(1)
            ser.write(b'lep\r')
            return ser
        except Exception as e:
            print(e)
            return None

    def get_position(self):
        if self.connection and self.connection.is_open:
            try:
                print("Sending position request to device...")
                self.connection.write(b'lep\r')
                time.sleep(1)
                response = self.connection.readline().decode('utf-8').strip()
                print(f"Received response: {response}")
                if response.startswith('POS'):
                    _, x, y, z, success_percentage = response.split(',')
                    position = {
                        'x': float(x),
                        'y': float(y),
                        'z': float(z),
                        'success_percentage': float(success_percentage),
                    }
                    print(f"Parsed position: {position}")
                    return position
            except Exception as e:
                print(f"Error while getting position: {e}")
        else:
            print("Connection is not open.")
        return None

    def has_traveled_more_than_segments(self):
        current_position = self.get_position()
        if not current_position or not self.initial_position:
            return False

        distance_x = abs(current_position['x'] - self.initial_position['x'])
        distance_y = abs(current_position['y'] - self.initial_position['y'])

        return distance_x > RECTANGLE_SEGMENTS[0] or distance_y > RECTANGLE_SEGMENTS[1]

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

