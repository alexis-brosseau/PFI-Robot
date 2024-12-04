import math
import math
from threading import Thread
from lisseur import Lisseur
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
    LIDAR_FOV = 40
    LIDAR_OFFSET = 160
    LIDAR_RANGE = 600
    CLAW_PINS = [16, 20, 21]  # GPIO pins for the claw
    RADIO_NAV_PIN = "/dev/ttyACM0" 
    RECTANGLE_SEGMENTS = [1, 0.5]  # 2 segments pour le rectangle que le robot va parcourir (2mx4m)
    TURN_BRAKE_OFFSET = 5  # Offset pour le freinage lors d'un virage (en degrés)

    def __init__(self):
        self.motor = Motor()
        self.end = False
        self.cv2 = cv2
        self.window = Window(self.cv2)
        self.window.add_screen('Plan', np.zeros((self.IMAGE_SIZE_X, self.IMAGE_SIZE_Y, 3), np.uint8))
        self.lidar = Lidar(self.LIDAR_PORT, self.LIDAR_FOV, self.LIDAR_RANGE, self.LIDAR_OFFSET)
        self.claw = Claw(self.CLAW_PINS)
        self.state = State().BRAKE
        self.orientation = Orientation()
        self.radio_navigation = RadioNavigation(self.RADIO_NAV_PIN)
        self.lisseur_distance = Lisseur(8)
        
    def afficher_info(self):
        while self.state != State().STOP:            
            time.sleep(0.25)
            card_index = round(self.orientation.ori_mag / 45) % 8
            print(f"\rRelative: {round(self.orientation.ori_rel, 2)}, Magnetique: {round(self.orientation.ori_mag, 2)} {Orientation.CARDINAUX[card_index]}   ", end="")
            
    def __go_forward(self):
        if self.lidar.obstacle_detecte:
            self.__brake()
            return

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
        initial_orientation = self.orientation.ori_rel
        target_orientation = initial_orientation + (90 - self.TURN_BRAKE_OFFSET)

        self.__turn_right()
        
        while self.orientation.ori_rel < target_orientation:
            time.sleep(0.01)
        self.__brake()
        
    
    def follow_rectangle(self):
        print(self.radio_navigation.initial_position)
        if not self.radio_navigation.initial_position:
            self.radio_navigation.initial_position = self.radio_navigation.get_position()
            return
        
        try:
            for segment_length in self.RECTANGLE_SEGMENTS * 2:  # Repeat [2, 1] twice
                print(f"Moving forward {segment_length} meters.")
                self.go_forward_until_distance(segment_length)
                print("Turning 90 degrees.")
                self.__turn_90_degrees()
            
            self.radio_navigation.initial_position = None
        except Exception as e:
            print(f"Error while following rectangle: {e}")
            
    def go_forward_until_distance(self, target_distance):
        start_position = self.radio_navigation.current_position
        self.lisseur_distance.renitialiser()
        if not start_position:
            start_position = self.radio_navigation.get_position()
            return
        
        while True:
            self.__go_forward()
            current_position = self.radio_navigation.current_position
            if not current_position:
                print("Lost connection to device while moving forward.")
                break
            
            # Calculate traveled distance
            traveled_x = abs(current_position['x'] - start_position['x'])
            traveled_y = abs(current_position['y'] - start_position['y'])
            self.lisseur_distance.ajouter(math.sqrt(traveled_x ** 2 + traveled_y ** 2),False)
            traveled_distance = self.lisseur_distance.moyenne
            
            if traveled_distance >= target_distance:
                print("Target distance reached.")
                self.__brake()
                break
    
    def __open_claw(self):
        self.claw.open()
        time.sleep(1)
    
    def __close_claw(self):
        self.claw.close()
        time.sleep(1)
            
    def __up_claw(self):
        self.claw.move_up()
        time.sleep(1)
    
    def __down_claw(self):
        self.claw.move_down()
        time.sleep(1)
    
    def __stop(self):
        self.lidar.stop_thread()
        self.motor.stop_motors()
        self.radio_navigation.close_connection()
        self.orientation.arreter()
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
            self.follow_rectangle()
        elif key==ord('c'):
            if self.claw.is_open:
                self.__close_claw()
            else:
                self.__open_claw()
        elif key==ord('v'):
            if self.claw.is_up:
                self.__down_claw()
            else:
                self.__up_claw()
        elif key==ord('x'):
            self.__stop()
            self.end = True

    def execute_program(self):

        self.lidar.on_obstacle(lambda robot = self: robot.__brake() if (robot.state == State.FORWARD) else None)

        self.orientation.demarrer()
        self.lidar.start_thread()
        self.radio_navigation.start_monitoring()
        
        while not self.end:
            self.__read_keys()
            self.window.display()