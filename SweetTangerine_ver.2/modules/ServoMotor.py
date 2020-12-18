# 서보모터 제어
# 캐퍼시터 미사용으로 오작동 발생

import RPi.GPIO as GPIO
from time import sleep
import threading

class Control_Servo_Motor:
    def __init__(self, EN, pwm):
        GPIO.setup(EN, GPIO.OUT)
        self.p = GPIO.PWM(EN, pwm)   
        self.p.start(0)
    
    def Change_Cycle(self, cycle):
        self.p.ChangeDutyCycle(cycle) 
        sleep(2) # 회전할 시간을 충분히 제공
        self.p.stop()

