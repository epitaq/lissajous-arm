

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
    def _ArcSinAngle (self, angle):
        return np.arcsin(np.radians(angle))
    def _ArcCosAngle (self, angle):
        return np.arccos(np.radians(angle))
    def _ArcTanAngle (self, angle):
        return np.arctan(np.radians(angle))

    # https://manabitimes.jp/math/1235
    # 直交座標系 (Orthogonal coordinate system) OCS
    # 極座標系（polar coordinates system）PCS
    def PCS2OCS (self, angle_0: float, angle_1: float, length: float) :
        """
            極座標から直交座標に変換する
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
            array型で直交座標を受けて極座標を返す
            -> array(angle_0, angle_1, r)
        """
        r = np.sqrt(sum([i**2 for i in xyz]))
        angle_0 = np.arctan(xyz[1] / xyz[0])
        angle_1 = np.arctan((np.sqrt(xyz[0]**2 + xyz[1]**2) / xyz[2]**2))
        return np.array(angle_0, angle_1, r)

    def Angle2EffectorPoint (self, angles: list[float]):
        """
            角度をとり、先端のベクトルを返す
            Effector:先端の位置
            angles: [servo0, servo1, servo2]
            -> [x, y, z]
        """
        # 並行になってる棒の長さの比
        # t = self.arm_length_2 / self.arm_length_0
        # arm_length_0_vector = self.PCS2OCS(angles[0], angles[2], self.arm_length_0)
        # effect pointに繋がってるベクトルとそれに繋がってるベクトルの和で表せる
        # effect pointに繋がってるベクトルは角度が繋がってない短い方のベクトルと同じだからその角度と自身の長さで求める
        arm_length_1_vector = self.PCS2OCS(angles[1], angles[2], self.arm_length_1)
        arm_length_2_vector = self.PCS2OCS(angles[0], angles[2], self.arm_length_2)
        
        return arm_length_1_vector + arm_length_2_vector
    
    # https://tajimarobotics.com/kinematics-two-link-model-2/
    def EffectorPoint2Angle (self, OCS:list[float]):
        """
            effector pointの三次元座標からサーボモーターの角度に変換する
            OCS: [x, y, z]
            -> [servo0, servo1, servo2]
        """
        x_3d, y_3d, z_3d = OCS # 3次元座標を展開
        # アーム回転面での回転角: arm_servo_2 相当 極座標系のφ
        # 直線上の時は0で割ることになる
        if x_3d**2 + y_3d**2 == 0:
            arm_servo_2 = 0
        else :
            arm_servo_2 = self._ArcCosAngle(x_3d / np.sqrt(x_3d**2 + y_3d**2)) 
        arm_servo_2 = np.degrees(arm_servo_2)

        # ここからは原点とz軸とeffector Pointを通る二次元平面
        # effector point の二次元ベクトル
        x_2d = np.sqrt(x_3d**2 + y_3d**2)
        y_2d = z_3d

        # サーボ1個めの角度
        arm_servo_0 = - self._ArcCosAngle(
            (x_2d**2 + y_2d**2 + self.arm_length_0**2 - self.arm_length_2**2) 
            / (2*self.arm_length_0 * np.sqrt(x_2d**2 + y_2d**2))
            + self._ArcTanAngle(x_2d / y_2d)
        )
        arm_servo_0 = np.degrees(arm_servo_0)
        # サーボ2個めの角度
        arm_servo_1 = self._ArcTanAngle(
            (x_2d - self.arm_length_0 * self._SinAngle(arm_servo_0)) 
            / (y_2d - self.arm_length_0 * self._CosAngle(arm_servo_0))
        )
        arm_servo_1 = np.degrees(arm_servo_1)
        return [arm_servo_0, arm_servo_1, arm_servo_2]





