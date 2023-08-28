import RPi.GPIO as GPIO

class Led:
    def __init__ (self):
        self.LED_PIN = 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_PIN,GPIO.OUT)
    
    def setLed (self, switch: bool):
        GPIO.output(self.LED_PIN, switch)
