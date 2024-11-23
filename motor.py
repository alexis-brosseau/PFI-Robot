from gpiozero import PWMOutputDevice, DigitalOutputDevice

class Motor:
    IN1 = 6
    IN2 = 5
    IN3 = 15
    IN4 = 14
    ENA = 13
    ENB = 18
    speed = 0.5
    TURN_SPEED = 0.65

    def __init__(self):
        self.motor_left = PWMOutputDevice(pin=self.ENA, frequency=1000)
        self.motor_right = PWMOutputDevice(pin=self.ENB, frequency=1000)
        self.motor_left.value = self.speed
        self.motor_right.value = self.speed
        
        self.forward_left = DigitalOutputDevice(pin=self.IN1) 
        self.backward_left = DigitalOutputDevice(pin=self.IN2)
        self.forward_right = DigitalOutputDevice(pin=self.IN3)
        self.backward_right = DigitalOutputDevice(pin=self.IN4)

    def move(self, forward_left, forward_right, backward_left, backward_right):
        self.forward_left.value = forward_left
        self.forward_right.value = forward_right
        self.backward_left.value = backward_left
        self.backward_right.value = backward_right

    def speed_up(self):
        if self.speed > 0.9 and self.speed < 1:
            self.speed = 1
        elif self.speed < 1:
            self.speed = self.speed + 0.1

        self.motor_left.value = self.speed
        self.motor_right.value = self.speed

    def speed_down(self):
        if self.speed < 0.1 and self.speed > 0:
            self.speed = 0
        elif self.speed > 0:
            self.speed = self.speed - 0.1

        self.motor_left.value = self.speed
        self.motor_right.value = self.speed

    def stop_motors(self):
        self.forward_left.off()
        self.forward_right.off() 
        self.backward_left.off()
        self.backward_right.off()

        self.motor_left.off()
        self.motor_right.off()

    def change_turn_speed(self):
        self.motor_left.value = self.TURN_SPEED
        self.motor_right.value = self.TURN_SPEED

    def change_normal_speed(self):
        self.motor_left.value = self.speed
        self.motor_right.value = self.speed