# 新しい方のライブラリ使う
# https://docs.circuitpython.org/projects/servokit/en/latest/
# https://qiita.com/hinemoss/items/770e2280d33278b594be
from adafruit_servokit import ServoKit

import numpy as np
import copy

import calculation

class Arm:
    '''
        ここではアーム動作を一つにまとめほかからはただの棒のようにみせる
    '''

    def __init__ (self, SERVO_CHANNELS, ARM_LENGTHS):
        # サーボの初期設定
        self.kit = ServoKit(channels=8)
        # sg90にパルスを揃える
        for channel in SERVO_CHANNELS.values():
            self.kit.servo[channel].set_pulse_width_range(500, 2400)
        
        self.SERVO_CHANNELS = SERVO_CHANNELS
        
        # アームの長さ
        self.head_arm_length = ARM_LENGTHS['head_arm_length']
        self.root_head_arm_length = ARM_LENGTHS['root_head_arm_length']
        self.root_link_arm_length = ARM_LENGTHS['root_link_arm_length']

        # アームの初期位置の設定
        self.kit.servo[SERVO_CHANNELS['root_link_servo']].angle = 90
        self.kit.servo[SERVO_CHANNELS['root_head_servo']].angle = 0

    def moveServos (self, angles= {'root_servo': -1,'head_servo':-1,'root_head_servo': -1,'root_link_servo': -1}):
        '''
            サーボをうごかす
            anglesは辞書型で入力する。-1の時は動かさない
        '''
        print('moveServos: ')
        print(angles)
        for id, channel in self.SERVO_CHANNELS.items():
            angle = angles[id]
            # サーボの取り付けによって補正が必要 
            # 追加するたびに getServoAnglesも変更 TODO
            if id == 'root_link_servo':
                angle = 180 - angle
            if angle != -1:
                self.kit.servo[channel].angle = angle
    
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
        between_angle = calculation.angleFromRotationRadius(
            rotation_radius = rotation_radius, 
            length_0 = self.root_head_arm_length, 
            length_1 = self.head_arm_length
        )
        print('between_angle: ' + str(between_angle))
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
            'head_servo': -1,
            'root_head_servo': root_head_servo,
            'root_link_servo': root_link_servo
        })

    def setAzimuthalAngle(self, azimuthal_angle: float):
        pass

    def setPolarAngle(self, polar_angle: float):
        pass

    def getPossiblePolarAngleRange(self, arm_length: float) -> list[int]:
        pass

    def searchFocalLengthContinuously(self, possible_range: list[int], search_range: list[int]) -> float:
        pass


class Arm_tmp :
    """
        りさじゅうのアームを動かす
    """

    def __init__ (self, SERVO_CHANNEL, ARM_LENGTH ):
        i2c = busio.I2C(SCL, SDA)

        # Create a simple PCA9685 class instance.
        pca = PCA9685(i2c)

        # サーボ動かす用のやつ
        # arm用
        arm_servo_0 = servo.Servo(pca.channels[SERVO_CHANNEL['arm0']])
        arm_servo_1 = servo.Servo(pca.channels[SERVO_CHANNEL['arm1']])
        arm_servo_2 = servo.Servo(pca.channels[SERVO_CHANNEL['arm2']])
        self.arm_servo = [arm_servo_0, arm_servo_1, arm_servo_2]
        # アタッチメント用
        attachment_servo_0 = servo.Servo(pca.channels[SERVO_CHANNEL['attachment0']])
        attachment_servo_1 = servo.Servo(pca.channels[SERVO_CHANNEL['attachment1']])
        self.attachment_servo = [attachment_servo_0, attachment_servo_1]


        # アームの長さ
        self.arm_length_0 = ARM_LENGTH['arm0'] # 支点につてる短い方
        self.arm_length_1 = ARM_LENGTH['arm1'] # 支点についてる長い方, arm2に繋がってる方
        self.arm_length_2 = ARM_LENGTH['arm2'] # arm0,1についてる方
        

    def MoveServosByAngle (self, servos: list[float], angles: list[float]):
        """
            角度のリストから複数のサーボの角度を変更する
        """
        for index, servo in enumerate(servos):
            servo.angle = angles[index]

    # sin cosの計算
    def _SinAngle (self, angle):
        return np.sin(np.radians(angle))
    def _CosAngle (self, angle):
        return np.cos(np.radians(angle))
    def _TanAngle (self, angle):
        return np.tan(np.radians(angle))
    def _ArcSinAngle (self, x):
        print('arcsin: ' + str(x))
        if x > 1: x = 1
        elif x < -1: x = -1
        return np.degrees(np.arcsin(x))
    def _ArcCosAngle (self, x):
        print('arccos: ' + str(x))
        if x > 1: x = 1
        elif x < -1: x = -1
        return np.degrees(np.arccos(x))
    def _ArcTanAngle (self, x):
        print('arctan: '+str(x))
        return np.degrees(np.arctan(x))

    # https://manabitimes.jp/math/1235
    # 直交座標系 (Orthogonal coordinate system) OCS
    # 球座標系（polar coordinates system）PCS
    def PCS2OCS (self, radial_distance: float, polar_angle: float, azimuthal_angle: float) :
        """
            球座標から直交座標に変換する
            polar_angle アーム動作面での原点とのなす角: 90-(arm_servo_0 | arm_servo_1)相当
            azimuthal_angle アーム回転面での回転角: arm_servo_2 相当
            array型で返す
            [x, y, z]
        """
        x = radial_distance * self._SinAngle(polar_angle) * self._CosAngle(azimuthal_angle)
        y = radial_distance * self._SinAngle(polar_angle) * self._SinAngle(azimuthal_angle)
        z = radial_distance * self._CosAngle(polar_angle)
        return np.array([x, y, z])

    # https://keisan.casio.jp/exec/system/1359512223
    def OCS2PCS (self, xyz):
        """
            array型で直交座標を受けて球座標を返す
            -> array(r, polar_angle, azimuthal_angle)
        """
        x, y, z = xyz
        # 長さ
        r = np.sqrt(x**2 + y**2 + z**2)
        # 角度の計算
        # polar_angle = self._ArcTanAngle(np.sqrt(x**2 + y**2) / z)
        polar_angle = self._ArcCosAngle(z / r)
        azimuthal_angle = self._ArcTanAngle(y / x)
        return np.array([r, polar_angle, azimuthal_angle])

    def Angle2EffectorPoint (self, angles: list[float]):
        """
            角度をとり、先端のベクトルを返す
            Effector:先端の位置
            angles: [servo0, servo1, servo2]
            -> [x, y, z]
        """
        # effect pointに繋がってるベクトルとそれに繋がってるベクトルの和で表せる
        # effect pointに繋がってるベクトルは角度が繋がってない短い方のベクトルと同じだからその角度と自身の長さで求める
        arm_length_1_vector = self.PCS2OCS(
            polar_angle=angles[1], 
            azimuthal_angle=angles[2], 
            radial_distance=self.arm_length_1
        )
        arm_length_2_vector = self.PCS2OCS(
            polar_angle=angles[0], 
            azimuthal_angle=angles[2], 
            radial_distance=self.arm_length_2
        )
        
        return arm_length_1_vector + arm_length_2_vector
    
    # https://tajimarobotics.com/kinematics-two-link-model-2/
    def EffectorPoint2Angle (self, OCS:list[float]):
        """
            effector pointの三次元座標からサーボモーターの角度に変換する
            OCS: [x, y, z]
            -> [servo0, servo1, servo2]
        """
        # TODO なんかlistの参照関連な気がする
        x_3d, y_3d, z_3d = OCS # 3次元座標を展開

        # アーム回転面での回転角: arm_servo_2 相当 球座標系のφ
        arm_servo_2 = self.OCS2PCS(OCS)[2] # 直交座標から球座標に変更しφを取得

        # ここからは原点とz軸とeffector Pointを通る二次元平面
        # effector point の二次元ベクトル
        x_2d = np.sqrt(x_3d**2 + y_3d**2)
        y_2d = z_3d
        # アームの長さ
        a = self.arm_length_0
        b = self.arm_length_2

        # サーボ1個めの角度
        # + self._ArcCosAngle は±どっちでも
        # TODO とりあえずここが怪しい、arccosの計算で定義域をこえる
        arm_servo_0 = self._ArcTanAngle(x_2d / y_2d) - self._ArcCosAngle(
            (x_2d**2 + y_2d**2 + a**2 - b**2) 
            / (2 * a * np.sqrt(x_2d**2 + y_2d**2))
        ) 
        # サーボ2個めの角度
        arm_servo_1 = self._ArcTanAngle(
            (x_2d - a * self._SinAngle(arm_servo_0)) 
            / (y_2d - a * self._CosAngle(arm_servo_0))
        )

        return [arm_servo_0, arm_servo_1, arm_servo_2]





