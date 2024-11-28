from threading import Thread
from motor import Motor
from radio_navigation import RadioNavigation
from window import Window
from lidar import Lidar
from orientation import Orientation
from claw import Claw
from state import State
import numpy as np
import cv2
import time

class Robot:
    PIN_ENC_LEFT = 27
    PIN_ENC_RIGHT = 22
    DISTANCE_TRAVEL = 100
    REFRESH_RATE = 100
    IMAGE_SIZE_X = 512
    IMAGE_SIZE_Y = 512
    LIDAR_PORT = "/dev/ttyUSB0"
    CLAW_PIN = "/dev/ttyUSB1" # A MODIFIER
    RADIO_NAV_PIN = "/dev/ttyUSB2" # A MODIFIER

    def __init__(self):
        self.motor = Motor()
        self.end = False

        self.cv2 = cv2
        self.window = Window(self.cv2)
        self.lidar = Lidar(self.LIDAR_PORT, self.window)
        self.claw = Claw(self.CLAW_PIN)
        self.state = State().STOP
        self.orientation = Orientation()
        self.radio_navigation = RadioNavigation("/dev/ttyUSB2")
        
    def afficher_info(self):
        while self.state != State().STOP:            
            time.sleep(0.25)
            card_index = round(self.orientation.ori_mag / 45) % 8
            print(f"\rRelative: {round(self.orientation.get_rotation_degrees, 2)}, Magnetique: {round(self.orientation.ori_mag, 2)} {Orientation.CARDINAUX[card_index]}   ", end="")
            
    def __go_forward(self):
        self.motor.change_normal_speed()
        self.motor.move(1,1,0,0)
        self.state = State.FORWARD


    def __go_backward(self):
        self.motor.change_normal_speed()
        self.motor.move(0,0,1,1)
        self.state = State.BACKWARD


    def __turn_right(self):
        self.motor.change_turn_speed()
        self.motor.move(0,1,1,0)
        self.state = State.TURN_RIGHT

    def __turn_left(self):
        self.motor.change_turn_speed()
        self.motor.move(1,0,0,1)
        self.state = State.TURN_LEFT

    def __brake(self):
        self.motor.move(0,0,0,0)
        self.state = State.BRAKE

    def __increase_speed(self):
        self.motor.change_normal_speed()
        self.motor.speed_up()

    def __decrease_speed(self):
        self.motor.change_normal_speed()
        self.motor.speed_down()
    
    def __turn_90_degrees(self):
        while self.orientation.ori_rel < 90:
            self.__turn_right()
        self.__brake()
    
    def __start_path(self):
        Thread(target=self.radio_navigation.has_traveled_more_than_segments).start()
        while(not self.radio_navigation.has_traveled_more_than_segments()):
            self.__go_forward()
            self.__turn_90_degrees()
            
        self.__brake()
        
        
        pass

    def __stop(self):
        self.lidar.stop_thread()
        self.motor.stop_motors()
        self.state = State.STOP
    
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
        elif key==ord('q'):
            self.__start_path()
        elif key==ord('x'):
            self.__stop()
            self.end = True

    def execute_program(self):
        self.lidar.start_thread()
        self.orientation.calibrer()
        input("Calibration, appuyez sur une touche pour continuer...")

        self.orientation.demarrer()
        Thread(target=self.afficher_info).start()
        input("Appuyez sur une touche pour arreter le robot...\n")

        while not self.end:
            self.__read_keys()
            self.window.display()
    