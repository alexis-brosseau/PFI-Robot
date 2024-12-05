import serial
import time
from dwm1001 import ActiveTag #https://pypi.org/project/pydwm1001
import threading

RECTANGLE_SEGMENTS = [2, 4]  # 2 segments pour le rectangle que le robot va parcourir (2mx4m)

class RadioNavigation:
    def __init__(self, port):
        self.port = port
        self.connection = self.connect_to_device(port)
        self.tag = None
        self.is_monitoring = False

        if (self.connection.is_open):
            self.tag = ActiveTag(self.connection)
            self.tag.start_position_reporting()
        
        self.initial_position = self.get_position()
        self.current_position = self.initial_position

    def connect_to_device(self, port):
        try:
            serial_handle = serial.Serial(port, baudrate=115_200)
            print("Serial connection opened.")
            return serial_handle
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return None

    def get_position(self):
        if self.tag:
            try:
                position =  self.tag.position
            except:
                return None
            return {
                'x': position.x_m,
                'y': position.y_m,
                'z': position.z_m,
                'success_percentage': position.quality
            }
        else:
            print("Serial connection is not open.")
        return None

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Serial connection closed.")
            
    def start_monitoring(self):
        if (self.is_monitoring):
            self.stop_monitoring()
        
        self.is_monitoring = True    
        self.monitoring_thread = threading.Thread(target=self.monitor_position)
        self.monitoring_thread.start()

    def stop_monitoring(self):
         self.is_monitoring = False
         self.monitoring_thread.join()
        

    def monitor_position(self):
        while self.is_monitoring:
            position = self.get_position()
            if position:
                self.current_position = position
            time.sleep(0.05)