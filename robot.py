from motor import Motor
from window import Window
from lidar import Lidar
from claw import Claw
import numpy as np
import cv2

class Robot:
    PIN_ENC_LEFT = 27
    PIN_ENC_RIGHT = 22
    DISTANCE_TRAVEL = 100
    REFRESH_RATE = 100
    IMAGE_SIZE_X = 512
    IMAGE_SIZE_Y = 512
    LIDAR_PORT = "/dev/ttyUSB0"

    def __init__(self):
        self.motor = Motor()
        self.end = False

        self.cv2 = cv2
        self.window = Window(self.cv2)
        self.lidar = Lidar(self.LIDAR_PORT, self.window)
        self.claw = Claw()

    def __go_forward(self):
        self.motor.change_normal_speed()
        self.motor.move(1,1,0,0)

    def __go_backward(self):
        self.motor.change_normal_speed()
        self.motor.move(0,0,1,1)

    def __turn_right(self):
        self.motor.change_turn_speed()
        self.motor.move(0,1,1,0)

    def __turn_left(self):
        self.motor.change_turn_speed()
        self.motor.move(1,0,0,1)

    def __brake(self):
        self.motor.move(0,0,0,0)

    def __increase_speed(self):
        self.motor.change_normal_speed()
        self.motor.speed_up()

    def __decrease_speed(self):
        self.motor.change_normal_speed()
        self.motor.speed_down()

    def __stop(self):
        self.lidar.stop_thread()
        self.motor.stop_motors()
    
    def __read_keys(self):
        key = self.cv2.waitKey(self.REFRESH_RATE)

        if key==ord('w'): 
            self.__go_forward()
        elif key==ord('s'):
            self.__go_backward()
        elif key==ord('a'):
            self.__turn_left()
        elif key==ord('d'):
            self.__turn_right()
        elif key==ord(' '):
            self.__brake()
        elif key==ord('.'):
            self.__increase_speed()
        elif key==ord(','):
            self.__decrease_speed()
        elif key==ord('x'):
            self.__stop()
            self.end = True

    def execute_program(self):
        self.lidar.start_thread()

        while not self.end:
            self.__read_keys()
            self.window.display()
    