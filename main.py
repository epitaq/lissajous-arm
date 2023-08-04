import arm

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

    # while True:
    #     # アームの位置を取得 角度 座標
    #     # カメラで異常がないか確認
    #     # IF 異常があったら
    #     # ELSE IF モード変更するか 警戒、攻撃
    #     # 繰り返し
    #     pass
    
    # # 終了

    arm1 = arm.Arm(SERVO_CHANNEL, ARM_LENGTH)
    print(arm1.AngleLength2vector(10,10,10) )
