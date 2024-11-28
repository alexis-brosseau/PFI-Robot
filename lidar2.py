import PyLidar3
import time
from threading import Thread
import numpy as np
import cv2 as cv
import math

FRAME_SIZE=512
CENTER = FRAME_SIZE // 2
SCALE= 0.2
ANGLE_OFFSET = 90

class Lidar:
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
            for obs in self.observateurs:
                obs(data)
            time.sleep(0.5)
        
        self.__obj.StopScanning()
        self.__obj.Disconnect()

    def arreter_scan(self):
        self.est_demarrer = False
        self.__thread.join()

    def demarrer_scan(self):
        if (self.est_demarrer):
            self.arreter_scan()
        self.est_demarrer = True
        self.__thread = Thread(target=self.__scan)
        self.__thread.start()

if __name__ == "__main__":

    img = np.zeros((FRAME_SIZE, FRAME_SIZE, 3), np.uint8)
    cv.imshow("Lidar", img)
    cv.waitKey(-1)

    def draw(data):
        img = np.zeros((FRAME_SIZE, FRAME_SIZE, 3), np.uint8) 
        for angle in range(0, 359):
            x = int(CENTER + data[angle] * SCALE * math.cos(math.radians((angle + ANGLE_OFFSET) % 360)))
            y = int(CENTER + data[angle] * SCALE * math.sin(math.radians((angle + ANGLE_OFFSET) % 360)))
            cv.circle(img, (x, y), 2, (0, 0, 255), -1)
        cv.imshow("Lidar", img)


    port = "/dev/ttyUSB0"
    lidar = Lidar(port)
    lidar.observateurs.append(lambda data: draw(data))

    lidar.demarrer_scan()
    cv.waitKey(-1)
    lidar.arreter_scan()