import PyLidar3
import time
from threading import Thread
import numpy as np
import cv2 as cv
import math

class Lidar:
    
    ANGLE_OFFSET = 90
    
    def __init__(self, port):
        self.__obj = PyLidar3.YdLidarX4(port) 
        self.__thread = None
        self.est_demarrer = False
        self.observateurs = []


    def __scan(self):
        if(self.__obj.Connect()):
            gen = self.__obj.StartScanning()
        else:
            print("Erreur")
            self.__obj.Reset()
            return
        
        while (self.est_demarrer):
            data = next(gen) # Dictionnaire: data[0:359]
            
            pos = []
            
            for angle in range(360):
                x = int(data[angle] * math.cos(math.radians((angle + self.ANGLE_OFFSET) % 360)))
                y = int(data[angle] * math.sin(math.radians((angle + self.ANGLE_OFFSET) % 360)))
                pos.append((x, y))
            
            for obs in self.observateurs:
                obs(pos)

            time.sleep(0.5)
        
        self.__obj.StopScanning()
        self.__obj.Disconnect()

    def stop_thread(self):
        self.est_demarrer = False
        self.__thread.join()

    def start_thread(self):
        if (self.est_demarrer):
            self.arreter_scan()
        self.est_demarrer = True
        self.__thread = Thread(target=self.__scan)
        self.__thread.start()