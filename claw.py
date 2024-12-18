from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

class Claw:
    def __init__(self, pins, min_pulse_width=1/1000, max_pulse_width=2/1000, host='localhost', port=8888):
        factory = PiGPIOFactory(host=host, port=port)
        self.is_open = False
        self.is_up = False
        self.servo_claw = Servo(
            pins[0],  # pin pince
            min_pulse_width=min_pulse_width, 
            max_pulse_width=max_pulse_width,
            pin_factory=factory
        )
        self.servo_up_down = Servo(
            pins[1],  # pin rotation
            min_pulse_width=min_pulse_width, 
            max_pulse_width=max_pulse_width,
            pin_factory=factory
        )
        self.servo_rotate = Servo(
            pins[2],  # pin up/down
            min_pulse_width=min_pulse_width, 
            max_pulse_width=max_pulse_width,
            pin_factory=factory
        )

    def open(self):
        print("Ouverture de la pince")
        self.servo_claw.max()
        self.is_open = True

    def close(self):
        print("Fermeture de la pince")
        self.servo_claw.min()
        self.is_open = False    
    
    def move_up(self):
        print("Montée de la pince")
        self.servo_up_down.max()
        self.is_up = True

    def move_down(self):
        print("Descente de la pince")
        self.servo_up_down.min()
        self.is_up = False
        
    def set_position(self, value):
        
        #value = -1: fermeture de la pince
        #value = 1: ouverture de la pince
        
        if -1 <= value <= 1:
            print(f"position de la pince à {value}")
            self.servo_claw.value = value
        else:
            raise ValueError("Position doit être entre 1 et -1")

    def detach(self):
        #Désactiver le contrôle de la pince
        self.servo_claw.detach()
        self.servo_rotate.detach()
        self.servo_up_down.detach()