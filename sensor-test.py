import RPi.GPIO as GPIO
import time
import sys 


# HIGH or LOWの時計測
def pulseIn(PIN, start=1, end=0):
    if start==0: end = 1
    t_start = 0
    t_end = 0
    # ECHO_PINがHIGHである時間を計測
    while GPIO.input(PIN) == end:
        t_start = time.time()
        
    while GPIO.input(PIN) == start:
        t_end = time.time()
    return t_end - t_start

# 距離計測
def calc_distance(TRIG_PIN, ECHO_PIN, v=34000):
    # TRIGピンを0.3[s]だけLOW
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.3)
    # TRIGピンを0.00001[s]だけ出力(超音波発射)        
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    # HIGHの時間計測
    t = pulseIn(ECHO_PIN)
    # 距離[cm] = 音速[cm/s] * 時間[s]/2
    distance = v * t/2
    print(distance, "cm")
    # ピン設定解除
    GPIO.cleanup()
    # cm -> mm
    distance *= 10 
    return distance

while True:
    try:
        # TRIGとECHOのGPIO番号   
        TRIG_PIN = 27
        ECHO_PIN = 18

        # 気温24[℃]の場合の音速[cm/s]
        v = 33150 + 60*24
        
        # ピン番号をGPIOで指定
        GPIO.setmode(GPIO.BCM)
        # TRIG_PINを出力, ECHO_PINを入力
        GPIO.setup(TRIG_PIN,GPIO.OUT)
        GPIO.setup(ECHO_PIN,GPIO.IN)
        GPIO.setwarnings(False)
            
        # 距離計測(TRIGピン番号, ECHO_PIN番号, 計測回数, 音速[cm/s])
        calc_distance(TRIG_PIN, ECHO_PIN, v)
        
        time.sleep(1)                          #1秒間待つ

    except KeyboardInterrupt:       #Ctrl+Cキーが押された
        GPIO.cleanup()              #GPIOをクリーンアップ
        sys.exit()                  #プログラム終了
        