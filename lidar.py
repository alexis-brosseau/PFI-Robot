import PyLidar3
import time
from threading import Thread
import numpy as np
import cv2 as cv
import math

class Lidar:
    
    def __init__(self, port, offset, fov, range):
        self.__obj = PyLidar3.YdLidarX4(port) 
        self.__thread = None
        self.est_demarrer = False
        self.listeners = []
        self.offset = offset
        self.fov = fov
        self.range = range


    def __scan(self):
        if(self.__obj.Connect()):
            gen = self.__obj.StartScanning()
        else:
            print("Erreur")
            self.__obj.Reset()
            return
        
        while (self.est_demarrer):
            data = next(gen) # Dictionnaire: data[0:359]
            
            for angle in range(Lidar.FOV):
                if (data[angle + self.offset] < self.range):
                    for listener in self.listeners:
                        listener()
                    
            time.sleep(0.5)
        
        self.__obj.StopScanning()
        self.__obj.Disconnect()

    def on_obstacle(self, callback):
        self.listeners.append(callback)

    def stop_thread(self):
        self.est_demarrer = False
        self.__thread.join()

    def start_thread(self):
        if (self.est_demarrer):
            self.arreter_scan()
        self.est_demarrer = True
        self.__thread = Thread(target=self.__scan)
        self.__thread.start()