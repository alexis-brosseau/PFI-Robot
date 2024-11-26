import PyLidar3
import time
from threading import Thread

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
    
    port = "/dev/ttyUSB0"
    lidar = Lidar(port)
    
    lidar.observateurs.append(lambda data: print(data))
    lidar.demarrer_scan()
    time.sleep(10)
    lidar.arreter_scan()