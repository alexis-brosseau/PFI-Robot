# Fait par Alexis Brosseau
# 31 oct. 2024

import time
import math
from threading import Thread
from icm20948 import ICM20948
from lisseur import Lisseur

class Orientation:
    
    IMMOBILE = 0
    ROTATION = 1
    CARDINAUX = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    
    def __init__(self):
        self.__imu = ICM20948()
        self.__lisseur_gx = Lisseur(5)
        self.__lisseur_my = Lisseur(200)
        self.__lisseur_mz = Lisseur(200)
        self.__rotation_data = [(0, 0), (0, 0)]
        self.__thread = None
        
        self.seuil_detection = 0.5
        self.is_active = False
        self.etat = self.IMMOBILE
        self.ori_rel = 0
        self.ori_mag = 0
        
    # Calibrer le magnetometre
    def __calibrer(self):
        while self.is_active:
            _, my, mz = self.__imu.read_magnetometer_data()
            self.__lisseur_my.ajouter(my)
            self.__lisseur_mz.ajouter(mz)
            time.sleep(0.05)
    
    def __main(self):
        
        # Correction des valeurs du magnetometre
        corr_my = 0 if len(self.__lisseur_my.data) < 2 else (max(self.__lisseur_my.data) + min(self.__lisseur_my.data)) / 2
        corr_mz = 0 if len(self.__lisseur_my.data) < 2 else (max(self.__lisseur_mz.data) + min(self.__lisseur_mz.data)) / 2
        
        while self.is_active:
            
            # Orientation relative
            _, _, _, gx, _, _ = self.__imu.read_accelerometer_gyro_data()
            ugx = gx - self.__lisseur_gx.moyenne
            
            if (abs(ugx) > self.seuil_detection): 
                # Rotation detectee               
                self.etat = self.ROTATION
            else:
                
                if (self.etat == self.ROTATION):
                    self.__rotation_data[1] = (ugx, time.time())
                    self.ori_rel += self.calc_rotation()
                    self.ori_rel = self.ori_rel % 360
                
                self.etat = self.IMMOBILE
            
            if self.etat == self.IMMOBILE:
                self.__lisseur_gx.ajouter(gx, False)
                self.__rotation_data[0] = self.__rotation_data[1] = (ugx, time.time())
            elif self.etat == self.ROTATION:
                self.__rotation_data[1] = (ugx, time.time())
                self.ori_rel += self.calc_rotation()
                self.ori_rel = self.ori_rel % 360
            
            # Orientation magnetique
            _, my, mz = self.__imu.read_magnetometer_data()
            umy = my - corr_my
            umz = mz - corr_mz
            self.ori_mag = math.atan2(umz, umy) * 180 / math.pi
            if (self.ori_mag < 0):
                self.ori_mag += 360
            
            time.sleep(0.05)

    def calc_rotation(self):

        sum_speed = self.__rotation_data[1][0] + self.__rotation_data[0][0]
        avg_speed = sum_speed / 2
        time_total = self.__rotation_data[1][1] - self.__rotation_data[0][1]
        
        self.__rotation_data[0] = self.__rotation_data[1]
        return avg_speed * time_total * -1
    
    def __demarrerThread(self, target):
        if (self.is_active):
            self.arreter()
        
        self.is_active = True
        self.__thread = Thread(target=target)
        self.__thread.start()
        
    def arreter(self):
        self.is_active = False
        self.__thread.join()
        
    def calibrer(self):
        self.__demarrerThread(self.__calibrer)
    
    def demarrer(self):
        self.__demarrerThread(self.__main)