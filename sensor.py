import RPi.GPIO as GPIO
import time
import sys 

class Sensor:
    def __init__ (self):
        # 以前の設定をリセット
        GPIO.cleanup()
        # TRIGとECHOのGPIO番号   
        self.TRIG_PIN = 27
        self.ECHO_PIN = 18
        # 気温24[℃]の場合の音速[cm/s]
        self.v = 33150 + 60*24
        # ピン番号をGPIOで指定
        GPIO.setmode(GPIO.BCM)
        # self.TRIG_PINを出力, self.ECHO_PINを入力
        GPIO.setup(self.TRIG_PIN,GPIO.OUT)
        GPIO.setup(self.ECHO_PIN,GPIO.IN)
        GPIO.setwarnings(False)

        print('Sensor [OK]')

    def pulseIn(self, PIN, start=1, end=0):
        if start==0: end = 1
        t_start = 0
        t_end = 0
        # self.ECHO_PINがHIGHである時間を計測
        while GPIO.input(PIN) == end:
            t_start = time.time()
            
        while GPIO.input(PIN) == start:
            t_end = time.time()
        return t_end - t_start

    # 距離計測
    def getDistance(self):
        # print('sensor: ')
        # TRIGピンを0.3[s]だけLOW
        GPIO.output(self.TRIG_PIN, GPIO.LOW)
        # time.sleep(0.3)
        # TRIGピンを0.00001[s]だけ出力(超音波発射)        
        GPIO.output(self.TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG_PIN, False)
        # HIGHの時間計測
        t = self.pulseIn(self.ECHO_PIN)
        # 距離[cm] = 音速[cm/s] * 時間[s]/2
        distance = self.v * t/2
        # cm -> mm
        distance *= 10 
        # print(f'  return: {distance/10}cm')
        return distance


# import sensor
# sens = sensor.Sensor()
# sens.getValue()