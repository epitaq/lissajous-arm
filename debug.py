import arm
import matplotlib
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d as art3d
import numpy as np

matplotlib.use('TkAgg')

class Debug(arm.Arm) :
    # ラズパイ関連の削除
    def __init__ (self, SERVO_CHANNEL, ARM_LENGTH ):
        # アームの長さ
        self.arm_length_0 = ARM_LENGTH['arm0'] # 支点につてる短い方
        self.arm_length_1 = ARM_LENGTH['arm1'] # 支点についてる長い方, arm2に繋がってる方
        self.arm_length_2 = ARM_LENGTH['arm2'] # arm0,1についてる方

    def Plt (self, angles, ax):
        """
            角度からアームのモデルを出力する
        """
        # fig = plt.figure()
        # ax = fig.add_subplot(projection='3d')
        # 軸
        r = 50
        for i in range(3):
            zero = np.zeros((3,2))
            zero[i][0] = r
            ax.plot(zero[0],zero[1],zero[2])
        # メイン描画
        # arm0
        arm = self._T([0,0,0], self.PCS2OCS(radial_distance=self.arm_length_0, polar_angle=angles[0], azimuthal_angle=angles[2]))
        ax.plot(arm[0], arm[1], arm[2])
        # arm1
        arm = self._T([0,0,0], self.PCS2OCS(radial_distance=self.arm_length_1, polar_angle=angles[1], azimuthal_angle=angles[2]))
        ax.plot(arm[0], arm[1], arm[2])
        # arm2
        arm = self._T(self.PCS2OCS(radial_distance=self.arm_length_1, polar_angle=angles[1], azimuthal_angle=angles[2]), 
                        self.Angle2EffectorPoint(angles))
        ax.plot(arm[0], arm[1], arm[2])
        # arm3
        arm = self._T(self.PCS2OCS(radial_distance=self.arm_length_0, polar_angle=angles[0], azimuthal_angle=angles[2]), 
                        self.PCS2OCS(radial_distance=self.arm_length_0, polar_angle=angles[0], azimuthal_angle=angles[2]) + self.PCS2OCS(radial_distance=self.arm_length_1, polar_angle=angles[1], azimuthal_angle=angles[2]))
        ax.plot(arm[0], arm[1], arm[2])
        # 描画範囲
        ax.set_xlim(-100,100)
        ax.set_ylim(-100,100)
        ax.set_zlim(0,100)
        # plt.show()
    
    def _T (self, list1, list2):
        return np.array([list1, list2]).T

def test (arm, angles, n):
    print('angles')
    print(angles)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    for i in range(n):
        arm.Plt(angles=angles, ax=ax)
        print('Angle2EffectorPoint')
        point = arm.Angle2EffectorPoint(angles)
        print([i for i in point])

        print('EffectorPoint2Angle ')
        ax.scatter(point[0],point[1],point[2], color=[0,0,0], alpha=(i)/(n))
        angles = arm.EffectorPoint2Angle(point)
        print([i for i in angles])

    plt.show()



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
        'arm0': 30, # 短い方
        'arm1': 100, # 長い方
        'arm2': 120 # 二つにくっついてる方
    }
    # インスタンス
    arm = Debug(SERVO_CHANNEL, ARM_LENGTH)

    # 繰り返しテスト
    angles = [-60,60,0]
    test(arm, angles, 4)
    arm.Plt(angles)

    # OCS2PCSが怪しい
    # while True:
    #     a =map(int, input('XYZ: ').split())
    #     b = arm.OCS2PCS(a)
    #     print('r: ',str(b[0]), 'θ: ',str(b[2]), 'φ: ',str(b[1]))

    # PCS2OCS
    # while True:
    #     a = list(map(int, input('r01: ').split()))
    #     b = arm.PCS2OCS(a[0],a[1],a[2])
    #     print(b)

    print(0)
