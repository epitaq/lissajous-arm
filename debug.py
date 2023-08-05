import arm

class Debug(arm.Arm) :
    # ラズパイ関連の削除
    def __init__ (self, SERVO_CHANNEL, ARM_LENGTH ):
        # i2c = busio.I2C(SCL, SDA)

        # # Create a simple PCA9685 class instance.
        # pca = PCA9685(i2c)

        # # サーボ動かす用のやつ
        # # arm用
        # arm_servo_0 = servo.Servo(pca.channels[SERVO_CHANNEL['arm0']])
        # arm_servo_1 = servo.Servo(pca.channels[SERVO_CHANNEL['arm1']])
        # arm_servo_2 = servo.Servo(pca.channels[SERVO_CHANNEL['arm2']])
        # self.arm_servo = [arm_servo_0, arm_servo_1, arm_servo_2]
        # # アタッチメント用
        # attachment_servo_0 = servo.Servo(pca.channels[SERVO_CHANNEL['attachment0']])
        # attachment_servo_1 = servo.Servo(pca.channels[SERVO_CHANNEL['attachment1']])
        # self.attachment_servo = [attachment_servo_0, attachment_servo_1]
        # アームの長さ
        self.arm_length_0 = ARM_LENGTH['arm0'] # 支点につてる短い方
        self.arm_length_1 = ARM_LENGTH['arm1'] # 支点についてる長い方, arm2に繋がってる方
        self.arm_length_2 = ARM_LENGTH['arm2'] # arm0,1についてる方
        

def test (arm, angles):
    print('angles')
    print(angles)

    for i in range(2):
        print('Angle2EffectorPoint')
        point = arm.Angle2EffectorPoint(angles)
        print(point)

        print('EffectorPoint2Angle ')
        angles = arm.EffectorPoint2Angle(point)
        print(angles)



if __name__ == '__main__':
    # 使用するサーボのチャンネル
    SERVO_CHANNEL = {
        'arm0': 0, # アーム直結0
        'arm1': 1, # アーム直結1
        'arm2': 2, # 根本
        'attachment0': 3,
        'attachment1': 4
        }
    # アームの長さ mm
    ARM_LENGTH = {
        'arm0': 60, # 短い方
        'arm1': 100, # 長い方
        'arm2': 100 # 二つにくっついてる方
    }

    arm = Debug(SERVO_CHANNEL, ARM_LENGTH)
    angles = [-60,60,0]
    # test(arm, angles)
    print(arm.OCS2PCS([20,43,20]))

    print(0)
