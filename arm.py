from board import SCL, SDA
import busio

from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

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
        

    def MoveServosByAngle (self, servos: list[int], angles: list[int]):
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

    # https://manabitimes.jp/math/1235
    # 直交座標系 (Orthogonal coordinate system) OCS
    # 極座標系（polar coordinates system）PCS
    def PCS2OCS (self, angle_0: int, angle_1: int, length: int) :
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
            (angle_0, angle_1, r)
        """
        r = np.sqrt(sum([i**2 for i in xyz]))
        angle_0 = np.arctan(xyz[1] / xyz[0])
        angle_1 = np.arctan((np.sqrt(xyz[0]**2 + xyz[1]**2) / xyz[2]**2))
        return np.array(angle_0, angle_1, r)

    def AngleLength2HeadPosition (self, angles: list[int]):
        """
            角度をとり、先端のベクトルを返す
            HeadPosition:先端の位置
            angles:角度
                [servo0, servo1, servo2]
        """
        # 並行になってる棒の長さの比
        # t = self.arm_length_2 / self.arm_length_0
        # arm_length_0_vector = self.PCS2OCS(angles[0], angles[2], self.arm_length_0)
        arm_length_1_vector = self.PCS2OCS(angles[1], angles[2], self.arm_length_1)
        arm_length_2_vector = self.PCS2OCS(angles[0], angles[2], self.arm_length_2)
        
        return arm_length_1_vector + arm_length_2_vector

