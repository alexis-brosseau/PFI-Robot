import PyLidar3
from threading import Thread
from window import Window
import time
from math import sin, cos
import numpy as np

class Lidar:
    
    ENVIRONMENT_WIDTH = 512
    ENVIRONMENT_LENGTH = 512
    ROBOT_POSITION = (256, 256)
    MAX_DISTANCE = 3000
    MIN_DISTANCE = 120
    RED = [0,0,255]
    GREEN = [0,255,0]

    def __init__(self, port, window : Window):
        self._obj = PyLidar3.YdLidarX4(port)
        self._scanning_thread = Thread(target=self._scan_area)
        self._flag = False
        self._window = window
        self._close_distance_threshold = 500 #distance where the robot can detect object in path
        
    def start_thread(self):
        self._scanning_thread.start()
    
    def stop_thread(self):
        self._flag = True
        self._stop_scanning()
        self._disconnect()
        self._scanning_thread.join()

    def set_gen(self):
        self._gen = self._obj.StartScanning()

    def get_gen(self):
        return self._gen
    
    def _stop_scanning(self):
        self._obj.StopScanning()

    def _is_connected(self):
        return self._obj.Connect()

    def _disconnect(self):
        self._obj.Disconnect()
        
    def _display_environment(self, numpy_array):
        self._window.add_screen('Plan', numpy_array)

    def _scan_area(self):
        if self._is_connected():
            self.set_gen()
            while not self._flag:
                try:
                    data = next(self.get_gen())
                    image = np.zeros((self.ENVIRONMENT_LENGTH, self.ENVIRONMENT_WIDTH, 3), dtype=np.uint8)
                    for angle, distance in data.items():
                        angle = np.radians(angle)
                        if distance > self.MIN_DISTANCE and distance < self.MAX_DISTANCE:
                            position = self._set_coordinates_pixel(angle, distance)
                            image = self._window.draw_circle(image, position, self.RED)
                    image = self._window.draw_circle(image, self.ROBOT_POSITION, self.GREEN)

                except Exception as error:
                    print(f'Une exception est survenue: {error}')
                finally:
                    self._display_environment(image)
                    time.sleep(1)
        else:
            print("Erreur de connexion.")
            self._obj.Reset()
    
    def _set_coordinates_pixel(self, angle, distance):
        x = self._convert_to_pixel(-distance * sin(angle))
        y = self._convert_to_pixel(distance * cos(angle))
        return x, y
    
    def _convert_to_pixel(self, point):
        return self.ROBOT_POSITION[0] + int(((self.ROBOT_POSITION[0] * point) / self.MAX_DISTANCE))
    
    def is_object_close(self):
        """
        Check if an object is close to the robot
        """
        if self._is_connected():
            try:
                data = next(self.get_gen())
                for angle, distance in data.items():
                    if self.MIN_DISTANCE < distance < self._close_distance_threshold:
                        print(f"Objet détecté proche! Angle: {angle}, Distance: {distance} mm")
                        return True
            except Exception as error:
                print(f"erreur s'est produite: {error}")
        return False