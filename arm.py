# 新しい方のライブラリ使う
# https://docs.circuitpython.org/projects/servokit/en/latest/
# https://qiita.com/hinemoss/items/770e2280d33278b594be
from adafruit_servokit import ServoKit

import numpy as np
import copy
import time

import calculation
import sensor

class Arm:
    '''
        ここではアーム動作を一つにまとめほかからはただの棒のようにみせる
    '''

    def __init__ (self, SERVO_CHANNELS, ARM_LENGTHS):
        # センサーの初期化
        self.sensor = sensor.Sensor()
        # サーボの初期設定
        self.kit = ServoKit(channels=16)
        # sg90にパルスを揃える
        for channel in SERVO_CHANNELS.values():
            self.kit.servo[channel].set_pulse_width_range(500, 2400)
        
        self.SERVO_CHANNELS = SERVO_CHANNELS
        
        # アームの長さ
        self.head_arm_length = ARM_LENGTHS['head_arm_length']
        self.root_head_arm_length = ARM_LENGTHS['root_head_arm_length']
        self.root_link_arm_length = ARM_LENGTHS['root_link_arm_length']

        # アームの初期位置の設定
        self.moveServos(angles={
            'root_servo': 0,
            'head_servo': 0,
            'root_head_servo': 0,
            'root_link_servo': 90}
        )

        # アーム同士がなす角
        self.arm_between_angle = 0
        # 合成ベクトルとアームのなす角
        self.composite_root_head_arm_angle = 0
        self.composite_root_link_arm_angle = 0

        # 動作可能な天頂角範囲
        self.possible_polar_angle_range = []
        
        print('Arm [OK]')

    def moveServos (self, angles= {'root_servo': -1,'head_servo':-1,'root_head_servo': -1,'root_link_servo': -1}):
        '''
            サーボをうごかす
            anglesは辞書型で入力する。-1の時は動かさない
        '''
        # print('moveServos: ',end=' ')
        # print(angles)
        for id, channel in self.SERVO_CHANNELS.items():
            angle = angles[id]
            if angle != -1 and not np.isnan(angle):
                # 範囲の制限
                if angle > 180: 
                    print('moveServo: over 180')
                    print('    current: ',str(angle))
                    angle=180
                elif angle < 0: 
                    print('moveServo: over 0')
                    print('    current: ',str(angle))
                    angle=0
                # サーボの取り付け向きによって補正が必要 
                # 追加するたびに getServoAnglesも変更 TODO
                if id == 'root_link_servo':
                    angle = 180 - angle
                self.kit.servo[channel].angle = angle
            # if id == 'head_servo':
            #     # 指示があるときはそれに従うがないときは自動で追尾する
            #     angle = 90 - self.composite_root_link_arm_angle
            #     self.kit.servo[channel].angle = angle
        # 早すぎて反動がきついから遅延
        # time.sleep(0.1)
        return

    def moveServosDifference (self, difference_angles= {'root_servo': 0,'head_servo': 0,'root_head_servo': 0,'root_link_servo': 0}):
        '''
            角度の差分からサーボをうごかす
            anglesは辞書型で入力する。
        '''
        print('moveServosDifference: ',end=' ')
        print(difference_angles)
        angles = copy.copy(self.SERVO_CHANNELS)
        current_angles_list = self.getServoAngles()
        for id, channel in self.SERVO_CHANNELS.items():
            difference_angle = difference_angles[id] # 差分
            current_angle = current_angles_list[id] # 現在の
            angles[id] = difference_angle + current_angle
            print('  servo difference: '+ id + str(difference_angle + current_angle))
        self.moveServos(angles=angles)
        return

    def getServoAngles (self):
        '''
            サーボの角度を取得する
            あまり精度はよくない
        '''
        angles = copy.copy(self.SERVO_CHANNELS)
        for id, channel in self.SERVO_CHANNELS.items():
            # サーボの角度
            angle = self.kit.servo[channel].angle
            # 0以下だとほかでバグるたぶん180でも
            if angle < 0: angle = 0
            elif angle > 180: angle=180
            # 実際の角度とサーボの角度変換 TODO
            if id == 'root_link_servo':
                angle = 180 - angle
            # 登録
            angles[id] = angle
        return angles

    def setRotationRadius(self, rotation_radius: float):
        '''
            アームが動作する半径に長さをセットする
        '''
        print('setRotationRadius: ', str(rotation_radius))
        between_angle = calculation.angleFromRotationRadius(
            rotation_radius = rotation_radius, 
            length_0 = self.root_head_arm_length, 
            length_1 = self.head_arm_length
        )
        # アームのなす角を保存
        self.arm_between_angle = between_angle
        # おかしい TODO
        self.composite_root_head_arm_angle = - calculation.arcCos(
            (self.root_head_arm_length + self.head_arm_length*calculation.cos(between_angle))
            / rotation_radius
        )
        self.composite_root_link_arm_angle = self.arm_between_angle + self.composite_root_head_arm_angle

        print('  between_angle: ' + str(between_angle))
        print('  composite_root_head_arm_angle: '+str(self.composite_root_head_arm_angle))
        print('  composite_root_link_arm_angle: '+str(self.composite_root_link_arm_angle))
        print('  head_servo: ' + str(90 - self.composite_root_link_arm_angle))

        angles = self.getServoAngles()
        root_head_servo = angles['root_head_servo']
        # root_head_servoを基準に指定の長さに変形する
        root_link_servo = between_angle + root_head_servo
        # 範囲をこえていた場合
        if root_link_servo < 0 : 
            # この場合は少ないはず、というか望ましくない
            root_head_servo -= root_link_servo
            root_link_servo = 0
        elif root_link_servo > 180 :
            root_head_servo -= root_link_servo - 180
            root_link_servo = 180
        # アームの変形
        self.moveServos({ 
            'root_servo': -1,
            'head_servo': 90 - self.composite_root_link_arm_angle,
            'root_head_servo': root_head_servo,
            'root_link_servo': root_link_servo
        })
        return

    def setAzimuthalAngle(self, azimuthal_angle: float):
        # channel = self.SERVO_CHANNELS['root_servo']
        # self.kit.servo[channel].angle = azimuthal_angle
        print('setAzimuthalAngle: ', str(azimuthal_angle))
        self.moveServos({ 
            'root_servo': azimuthal_angle,
            'head_servo': -1,
            'root_head_servo': -1,
            'root_link_servo': -1
        })
        return

    def setPolarAngle(self, polar_angle: float):
        print('setPolarAngle: ', str(polar_angle))
        root_head_servo = polar_angle + self.composite_root_head_arm_angle
        root_link_servo = polar_angle + self.composite_root_link_arm_angle
        # print('root_head_servo: '+ str(root_head_servo))
        # print('root_link_servo: '+ str(root_link_servo))
        self.moveServos({ 
            'root_servo': -1,
            'head_servo': -1,
            'root_head_servo': root_head_servo,
            'root_link_servo': root_link_servo
        })
        return

    def getPossiblePolarAngleRange(self) -> list[int]:
        '''
            変更可能な天頂角の範囲リストを返す
        '''
        min_range = - int(self.composite_root_head_arm_angle)
        max_range = int(180-self.composite_root_link_arm_angle)
        angle_range = [min_range, max_range]
        # 保存
        self.possible_polar_angle_range = angle_range
        return angle_range

    def searchFocalLengthContinuously(self, search_range: list[int], sensor_threshold: float) -> float:
        '''
            連続的にサーボをうごかし焦点距離を探る
            反応なかったら０を返す
            sensor_threshold:センサーの閾値
        '''
        print('searchFocalLengthContinuously: ')
        print('  search_range: ',end=' ')
        print(search_range)
        print('  sensor_threshold: ',str(sensor_threshold))
        min_range = max(self.possible_polar_angle_range[0], search_range[0])
        max_range = min(self.possible_polar_angle_range[1], search_range[1])
        print('  min&max_range: ',str(min_range),str(max_range))
        for angle in range(min_range, max_range,5):
            self.setPolarAngle(angle)
            # 超音波センサーの値を取得 [mm]
            sensor_value: float = self.sensor.getDistance()
            if sensor_value < sensor_threshold:
                print('  return: ', str(angle))
                return angle
        else:
            return 0