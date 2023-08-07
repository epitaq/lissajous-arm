try:
    from board import SCL, SDA
    import busio
    from adafruit_motor import servo
    from adafruit_pca9685 import PCA9685
except NotImplementedError as e:
    print(e)

import numpy as np

class Arm :
    """
        りさじゅうのアームを動かす
        (arm | attachment)_(servo | length)_`unique`
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
    def PCS2OCS (self, length: float, angle_0: float, angle_1: float) :
        """
            球座標から直交座標に変換する
            angle_0 アーム動作面での原点とのなす角: 90-(arm_servo_0 | arm_servo_1)相当
            angle_1 アーム回転面での回転角: arm_servo_2 相当
            array型で返す
            [x, y, z]
        """
        x = length * self._SinAngle(angle_0) * self._CosAngle(angle_1)
        y = length * self._SinAngle(angle_0) * self._SinAngle(angle_1)
        z = length * self._CosAngle(angle_0)
        return np.array([x, y, z])

    # https://keisan.casio.jp/exec/system/1359512223
    def OCS2PCS (self, xyz):
        """
            array型で直交座標を受けて球座標を返す
            -> array(r, angle_0, angle_1)
        """
        x, y, z = xyz
        # 長さ
        r = np.sqrt(x**2 + y**2 + z**2)
        # 角度の計算
        # angle_0 = self._ArcTanAngle(np.sqrt(x**2 + y**2) / z)
        angle_0 = self._ArcCosAngle(z / r)
        angle_1 = self._ArcTanAngle(y / x)
        return np.array([r, angle_0, angle_1])

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
            angle_0=angles[1], 
            angle_1=angles[2], 
            length=self.arm_length_1
        )
        arm_length_2_vector = self.PCS2OCS(
            angle_0=angles[0], 
            angle_1=angles[2], 
            length=self.arm_length_2
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





