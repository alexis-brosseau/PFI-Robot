from threading import Thread
import serial
import time
import math

class RadioNavigation:
    def __init__(self, port):
        self.port = port
        self.connection = self.connect_to_device(port)
        self.initial_position = self.get_position()

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

    def follow_rectangle(self):
        if not self.initial_position:
            print("Position initiale pas trouvée.")
            return
        try:
            for segment_length in RECTANGLE_SEGMENTS * 2:  # loop à travers les 2 segments du rectangle 2x
                print(f"Moving forward {segment_length} meters.")
                self.go_forward_until_distance(segment_length)
                print("Turning 90 degrees.")
                self.__turn_90_degrees()
        except Exception as e:
            print(f"Error while following rectangle: {e}")

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

