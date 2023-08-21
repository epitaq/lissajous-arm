import arm
import camera
import sensor
import calculation

import numpy as np

if __name__ == '__main__':
# SERVO_CHANNELS = {'root_servo': 0,'head_servo': 1,'root_head_servo': 2,'root_link_servo': 3}
# ARM_LENGTHS = {'head_arm_length': 120,'root_head_arm_length': 100,'root_link_arm_length': 30}
    SERVO_CHANNELS = {
        'root_servo': 0,
        'head_servo': 4,
        'root_head_servo': 8,
        'root_link_servo': 12
    }
    ARM_LENGTHS = {
        'head_arm_length': 200,
        'root_head_arm_length': 200,
        'root_link_arm_length': 50
    }

    camera = camera.Camera()
    arm = arm.Arm(
        SERVO_CHANNELS=SERVO_CHANNELS,
        ARM_LENGTHS=ARM_LENGTHS
    )
    sensor = sensor.Sensor()
    # calculation = calculation.Calculation()
    print('instance [OK]')

    # センサーに反応があった時追跡する範囲
    TRACKING_RANGE = 400
    # 見つからなかった時用の予備の探索範囲 [angle]
    SUB_SEARCH_RANGE = 10
    # ピンホールカメラでいう焦点距離
    focal_length_list: list[float] = []
    # アームをどの長さで動かすのか[mm] TODO 可変式にしたい
    rotation_radius: float = 300.0

    print('start lissajous-arm')
    while True:
        # カメラから画像での手の二次元座標を取得[pixel]
        # 画像の中心を0とする
        picture_coordinates: list[float] = camera.getPictureCoordinates() 
        # 超音波センサーの閾値 [mm]
        sensor_threshold: float = TRACKING_RANGE - rotation_radius

        # カメラに手の反応があった時
        if picture_coordinates:
            print('target [OK]')
            # 画像の二次元座標からアームのz軸方向の回転を決定＆移動
            # 回転したできた新たな二次元座標の軸をxy軸とする
            # TODO マイナスの値でてる
            arm_azimuthal_angle = calculation.azimuthalAngle(
                x = picture_coordinates[0],
                y = picture_coordinates[1]
            )
            arm.setAzimuthalAngle(azimuthal_angle = arm_azimuthal_angle)
            # アームの回転半径をせっと
            arm.setRotationRadius(
                rotation_radius=rotation_radius
            )
            # アームがxy軸とどれくらい角度を取れるのか[angle]
            arm_possible_polar_angle_range: list[int] = arm.getPossiblePolarAngleRange()
            # アームを動かし超音波センサーに反応があった時手を見つけたことにする
            # focal_length_listがない時、つまり初回
            if not focal_length_list:
                print('focal_length_list [FAILED]')
                # アームを連続的に動かして焦点距離を特定＆動く
                arm_current_polar_angle = arm.searchFocalLengthContinuously(
                    search_range = arm_possible_polar_angle_range,
                    sensor_threshold = sensor_threshold                
                )
                if arm_current_polar_angle == 0:
                    # 何もなかった時の処理入れる？ TODO
                    continue
                current_focal_length = calculation.getFocalLength(
                        picture_coordinates = picture_coordinates,
                        polar_angle = arm_current_polar_angle                    
                    )
                # 求めたfocal_lengthを記録
                focal_length_list.append(current_focal_length)
            # focal_length_listがある時はそれを元に移動し確かめる
            else:
                print('focal_length_list [OK]')
                # 今までのfocal_lengthからxy軸との角度を求める
                arm_polar_angle = calculation.getPolarAngleFromFocalLength(
                    picture_coordinates = picture_coordinates,
                    focal_length = sum(focal_length_list)/len(focal_length_list)                
                )
                # 移動
                arm.setPolarAngle(polar_angle = arm_polar_angle)
                # センサーの値を取得[mm]
                sensor_value: float = sensor.getDistance()
                # 反応した時はそのままfocalLengthに入れる
                if sensor_value <= sensor_threshold:
                    current_focal_length = calculation.getFocalLength(
                            picture_coordinates = picture_coordinates,
                            polar_angle = arm_polar_angle                        
                        )
                    focal_length_list.append(current_focal_length)
                    continue
                # してない時は少し探索する
                else:
                    # TODO focal_length_listを初期化した方がいいか
                    # アームを連続的に動かして焦点距離を特定＆動く
                    arm_current_polar_angle = arm.searchFocalLengthContinuously(
                        search_range = [np.floor(arm_polar_angle - SUB_SEARCH_RANGE), np.ceil(arm_polar_angle + SUB_SEARCH_RANGE), ],
                        sensor_threshold = sensor_threshold                    
                    )
                    if arm_current_polar_angle == 0:
                        # 何もなかった時の処理入れる？ TODO
                        break
                    current_focal_length = calculation.getFocalLength(
                        picture_coordinates = picture_coordinates,
                        polar_angle = arm_current_polar_angle                    
                    )
                    # 求めたfocal_lengthを記録
                    focal_length_list.append(current_focal_length)
        else:
            print('target [FAILED]')
            # TODO 初期状態どうする？
            pass

















