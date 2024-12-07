import PyLidar3
import time
from threading import Thread
import numpy as np
import cv2 as cv
import math

FRAME_SIZE=512
CENTER = FRAME_SIZE // 2
SCALE= 0.2
ANGLE_CERCLE = 360
ANGLE_DROIT = 90

class Lidar:
    
    def __init__(self, port, fov, range, offset = 0, treshold = 20, refresh_rate = 0.1):
        self.__obj = PyLidar3.YdLidarX4(port) 
        self.__thread = None
        self.__listeners = []
        self.est_demarrer = False
        self.obstacle_detecte = False
        self.offset = offset
        self.fov = fov
        self.range = range
        self.treshold = treshold
        self.refresh_rate = refresh_rate

    def __scan(self):
        if(self.__obj.Connect()):
            gen = self.__obj.StartScanning()
        else:
            print("Erreur")
            self.__obj.Reset()
            return
        
        while (self.est_demarrer):
            data = next(gen) # Dictionnaire: data[0:359]
            
            num_obstacle = 0

            for angle in range(0, self.fov):
                if (data[(angle + self.offset) % 360] < self.range):
                    num_obstacle += 1

            self.obstacle_detecte = num_obstacle >= self.treshold

            if (self.obstacle_detecte):
                for callback in self.__listeners:
                    callback()

            time.sleep(self.refresh_rate)
        
        self.__obj.StopScanning()
        self.__obj.Disconnect()

    def on_obstacle(self, callback):
        self.__listeners.append(callback)
    def stop_thread(self):
        self.est_demarrer = False
        self.__thread.join()

    def start_thread(self):
        if (self.est_demarrer):
            self.stop_thread()
        self.est_demarrer = True
        self.__thread = Thread(target=self.__scan)
        self.__thread.start()
