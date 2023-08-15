# TODO import センサーモジュール
import RPi.GPIO as GPIO

class Sensor:
    def __init__ (self):
        self.sw_pin = 18
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print('Sensor [OK]')

    def getValue(self) -> float:
        sw_status = GPIO.input(self.sw_pin)
        if sw_status == 0:
            # ON
            # 近い距離
            value = 10
        else:
            # OFF
            # 遠い距離
            value = 100000
        return value

# import sensor
# sens = sensor.Sensor()
# sens.getValue()