import RPi.GPIO as GPIO
import threading
from time import sleep
import sys
from modules.Buzzer import *
from modules.Class_Hx711 import *
from modules.DCMotor import *
from modules.I2C_LCD_driver import *
from modules.ServoMotor import *
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
    
import cv2
import socket
import numpy as np
import random

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.weight = 0
        self.btn1.clicked.connect(self.belt_Forward)
        self.btn2.clicked.connect(self.belt_Stop)
        self.btn3.clicked.connect(self.get_Weight)
        self.btn4.clicked.connect(self.anticlockwise)
        self.btn5.clicked.connect(self.clockwise)
        self.btn6.clicked.connect(self.start_system)
        
    def initUI(self):
        self.btn1 = QPushButton('&Belt Forward', self)
        self.btn2 = QPushButton('&Belt Stop', self)
        self.btn3 = QPushButton('&Get Weight', self)
        self.btn4 = QPushButton('&Servo_Anticlockwise', self)
        self.btn5 = QPushButton('&Servo_Clockwise', self)
        self.btn6 = QPushButton('&System Start', self)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.btn2)
        vbox.addWidget(self.btn3)
        vbox.addWidget(self.btn4)
        vbox.addWidget(self.btn5)
        vbox.addWidget(self.btn6)
        
        self.setLayout(vbox)
        self.setWindowTitle('Conveyor Classification')
        self.setGeometry(300, 300, 300, 200)
        self.show()
        
    def belt_Forward(self):
        cont_dc.setMotorControl(50, 'FORWARD')
    
    def belt_Stop(self):
        cont_dc.setMotorControl(50, 'STOP')
        
    def get_Weight(self):
        self.weight = gw.measure_Weight()
        if(self.weight <= 0):
            self.weight = 0
        else:
            self.weight = self.weight/450
        print(self.weight,'g')
        
    def anticlockwise(self):
        sermo = Control_Servo_Motor(18, 50)
        sermo.Change_Cycle(3)
        
    def clockwise(self):
        sermo = Control_Servo_Motor(18, 50)
        sermo.Change_Cycle(9)
    
    def start_system(self):
        try:
			# LCD init
            mylcd.lcd_display_string("        ",1) 
			
			# belt forwarding
            cont_dc.setMotorControl(50, 'FORWARD')
            sleep(1.9)
			
			# belt stop, classification start
            cont_dc.setMotorControl(50, 'STOP')
			
			# get sweetie
            sweetie = random.randrange(10,15)
            #print(sweetie)
			
			# sweetie output to lcd
            mylcd.lcd_display_string(str(sweetie),1)  
            
			# raspberry pie cam init
            cam = cv2.VideoCapture(0)
            cam.set(3, 1600);
            cam.set(4, 1200);
            
			# change quality
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]

			# get picture
            ret, frame = cam.read()
			
			# encoding
            result, frame = cv2.imencode('.png', frame, encode_param)
            data = np.array(frame)
            stringData = data.tostring()
            
			# send to server
            s.sendall((str(len(stringData))).encode().ljust(16) + stringData)
            
            cam.release()
            
			# restart belt for classification
            cont_dc.setMotorControl(50, 'FORWARD')
                  
            if sweetie <= 12:
                self.clockwise()
            else:
                self.anticlockwise()
            
            sleep(5)
            
            cont_dc.setMotorControl(50, 'STOP')
            
			# send sweetie, weight to server
            sendData = str(self.weight) +" "+ str(sweetie)
            s.sendall(sendData.encode())
            
			# receive fruits name
            recvData = s.recv(1024)
            fruitsname = recvData.decode()
			
            if fruitsname == 'tomato':
                print('Not Tangerine!')
                buz.buzzer_On()
                sleep(3)
                buz.buzzer_Off()
            
        except :
			# alarm
            print("System Error")
            buz.buzzer_On()
            sleep(3)
            buz.buzzer_Off()
        
    
if __name__ == '__main__':
    #set BCM mode
    GPIO.setmode(GPIO.BCM)
	
	# create object
    mylcd = lcd()
    gw = Get_Weight()
    buz = Buzzer_Control(23)

    ENA = 26
    IN1 = 19
    IN2 = 13
    
    cont_dc = Control_DC_Motor(ENA, IN1, IN2)
    
	# tcp init
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
    s.connect(('192.168.100.91', 8494))
        
	# pyqt init
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
    GPIO.cleanup()
    
    
