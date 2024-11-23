from gpiozero import Servo
from time import sleep

#Vu qu'il y a plusieurs pinces, va falloir tester les Value en classe lol
#Je crois qu'il y a un servo pour chaque pince (monter/descendre, ouvrir/fermer, droite/gauche)
#Faudra trouver la pin de la pince, parce que sinon la création marchera pas (pince créée dans robot.py)


class Claw:
    def __init__(self, pin, min_pulse_width=1/1000, max_pulse_width=2/1000):
        self.servo = Servo(
            pin, 
            min_pulse_width=min_pulse_width, 
            max_pulse_width=max_pulse_width
        )

    def open(self):
        print("Ouverture de la pince")
        self.servo.max()

    def close(self):
        print("Fermeture de la pince")
        self.servo.min()
        
    def set_position(self, value):
        """
        value = -1: fermeture de la pince
        value = 1: ouverture de la pince
        """
        if -1 <= value <= 1:
            print(f"position de la pince à {value}")
            self.servo.value = value
        else:
            raise ValueError("Position doit être entre 1 et -1")

    def detach(self):
        """Désactiver le contrôle de la pince"""
        self.servo.detach()