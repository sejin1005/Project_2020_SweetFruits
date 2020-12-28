# 컨베이어 벨트 DC 모터 제어

import RPi.GPIO as GPIO
from time import *

class Control_DC_Motor:
    def __init__(self, ENA, IN1, IN2) :
        GPIO.setup(ENA, GPIO.OUT)
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)

        self.IN1 = IN1
        self.IN2 = IN2
        self.pwm = GPIO.PWM(ENA,50)
        self.pwm.start(0)
    
    def setMotorControl(self, speed, stat):
        self.pwm.ChangeDutyCycle(speed)

        if stat == 'FORWARD': # 정방향 회전
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            
        
        elif stat == 'STOP': # 정지
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.LOW)
    
if __name__ == '__main__':
    #set BCM mode
    GPIO.setmode(GPIO.BCM)

    STOP = 0
    FORWARD = 1

    ENA = 26
    IN1 = 19
    IN2 = 13
    
    cont_dc = Control_DC_Motor(ENA, IN1, IN2)
    try:
        cont_dc.setMotorControl(30, 'FORWARD')
        sleep(10) # 모터가 돌아갈 시간을 충분히 제공
        #cont_dc.setMotorControl(70, 'STOP')
    except:
        pass
    finally:
        GPIO.cleanup()