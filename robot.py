import math
import math
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
    LIDAR_FOV = 60
    LIDAR_OFFSET = 150
    LIDAR_RANGE = 600
    CLAW_PINS = [16, 20, 21]  # GPIO pins for the claw
    RADIO_NAV_PIN = "/dev/ttyACM0" 
    RECTANGLE_SEGMENTS = [1, 2]  # 2 segments pour le rectangle que le robot va parcourir (2mx4m)

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
        while self.orientation.ori_rel < 90:
            self.__turn_right()
        self.__brake()
    
    def follow_rectangle(self):
        print(self.radio_navigation.initial_position)
        if not self.radio_navigation.initial_position:
            print("Initial position not set. Cannot follow the rectangle.")
            return
        
        try:
            for segment_length in self.RECTANGLE_SEGMENTS * 2:  # Repeat [2, 4] twice
                print(f"Moving forward {segment_length} meters.")
                self.go_forward_until_distance(segment_length)
                print("Turning 90 degrees.")
                self.__turn_90_degrees()
        except Exception as e:
            print(f"Error while following rectangle: {e}")
            
    def go_forward_until_distance(self, target_distance):
        start_position = self.radio_navigation.get_position()
        if not start_position:
            print("Cannot determine start position. Aborting forward movement.")
            return
        
        while True:
            self.__go_forward()
            current_position = self.radio_navigation.get_position()
            if not current_position:
                print("Lost connection to device while moving forward.")
                break
            
            # Calculate traveled distance
            traveled_x = abs(current_position['x'] - start_position['x'])
            traveled_y = abs(current_position['y'] - start_position['y'])
            traveled_distance = math.sqrt(traveled_x * 2 + traveled_y * 2)
            
            print(f"Traveled distance: {traveled_distance:.2f} meters.")
            if traveled_distance >= target_distance:
                print("Target distance reached.")
                break
    
    def __open_claw(self):
        self.claw.open()
        time.sleep(1)
    
    def __close_claw(self):
        self.claw.close()
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
            self.__open_claw()
        elif key==ord('x'):
            self.__stop()
            self.end = True

    def execute_program(self):

        self.lidar.on_obstacle(lambda robot = self: robot.__brake() if (robot.state == State.FORWARD) else None)
        self.lidar.on_obstacle(lambda: print("Obstacle"))

        self.orientation.calibrer()
        self.orientation.demarrer()
        self.lidar.start_thread()
        
        # Thread(target=self.afficher_info).start()
        while not self.end:
            self.__read_keys()
            self.window.display()