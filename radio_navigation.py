import serial
import time

RECTANGLE_SEGMENTS = [2,4] # 2 segments pour le rectangle que le robot va parcourir (2mx4m)
class RadioNavigation:
    def __init__(self, port):
        self.port = port
        self.connection = self.connect_to_device(port)

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
            ser.write(b'lep\r') #Pour rebasculer en mode csv, pas sur que ca marche
            return None

    def get_position(self):
        if self.connection and self.connection.is_open:
            try:
                self.connection.write(b'lep\r')
                time.sleep(1)
                response = self.connection.readline()
                _, x, y, z, angle = response.split(',')
                return {
                    'x': float(x),
                    'y': float(y),
                    'z': float(z),
                }
            except Exception as e:
                print(e)
        return None

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
