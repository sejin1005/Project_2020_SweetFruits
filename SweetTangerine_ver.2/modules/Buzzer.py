# Buzzer 제어
# High 신호 -> Buzzer 울림
# Low 신호 -> Buzzer 안울림
import RPi.GPIO as GPIO
from time import sleep

class Buzzer_Control:
    def __init__(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        self.pin = pin
    def buzzer_On(self):
        GPIO.output(self.pin, GPIO.HIGH)
    def buzzer_Off(self):
        GPIO.output(self.pin, GPIO.LOW)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)

    buz = Buzzer_Control(23)

    buz.buzzer_On()
    sleep(1)
    buz.buzzer_Off()
    sleep(1)