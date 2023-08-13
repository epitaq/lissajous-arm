import arm
import camera
import sensor
import calculation


if __name__ == '__main__':
# SERVO_CHANNELS = {'root_servo': 0,'head_servo': 1,'root_head_servo': 2,'root_link_servo': 3}
# ARM_LENGTHS = {'head_arm_length': 120,'root_head_arm_length': 100,'root_link_arm_length': 30}
    SERVO_CHANNELS = {
        'root_servo': 0,
        'head_servo': 1,
        'root_head_servo': 2,
        'root_link_servo': 3
    }
    ARM_LENGTHS = {
        'head_arm_length': 220,
        'root_head_arm_length': 210,
        'root_link_arm_length': 85
    }

    camera = camera.Camera()
    arm = arm.Arm()
    sensor = sensor.Sensor()
    # calculation = calculation.Calculation()

    # センサーに反応があった時追跡する範囲
    TRACKING_RANGE = 300
    # 見つからなかった時用の予備の探索範囲 [angle]
    SUB_SEARCH_RANGE = 10
    # ピンホールカメラでいう焦点距離
    focal_length_list: list[float] = []
    # アームをどの長さで動かすのか[mm] TODO 可変式にしたい
    rotation_radius: float = 100.0

    while True:
        # カメラから画像での手の二次元座標を取得[pixel]
        # 画像の中心を0とする
        picture_coordinates: list[float] = camera.getPictureCoordinates() 
        # アームの回転半径をせっと
        arm.setRotationRadius(
            rotation_radius=rotation_radius
        )
        # 画像の二次元座標からアームのz軸方向の回転を決定＆移動
        # 回転したできた新たな二次元座標の軸をxy軸とする
        arm_azimuthal_angle = calculation.azimuthalAngle(
            x = picture_coordinates[0],
            y = picture_coordinates[1]
        )
        arm.setAzimuthalAngle(azimuthal_angle = arm_azimuthal_angle)
        # アームがxy軸とどれくらい角度を取れるのか[angle]
        arm_possible_polar_angles: list[int] = arm.getPossiblePolarAngleRange(
            arm_length = rotation_radius
        )
        # 超音波センサーの閾値 [mm]
        sensor_threshold: float = TRACKING_RANGE - rotation_radius

        # カメラに手の反応があった時
        if len(picture_coordinates) != 0 :
            # アームを動かし超音波センサーに反応があった時手を見つけたことにする
            # focal_length_listがない時、つまり初回
            if len(focal_length_list) == 0:
                # アームを連続的に動かして焦点距離を特定＆動く
                new_focal_length = arm.searchFocalLengthContinuously(
                    possible_range = arm_possible_polar_angles,
                    search_range = arm_possible_polar_angles
                )
                # 求めたfocal_lengthを記録
                focal_length_list.append(new_focal_length)
                # for angle in range(arm_possible_polar_angles):
                #     # アームを指定の角度に動かす
                #     # 基準はxy軸
                #     arm.setPolarAngle(angle=angle)
                #     # 超音波センサーの値を取得 [mm]
                #     sensor_value: float = sensor.getValue()
                #     if sensor_value <= sensor_threshold:
                #         new_focal_length = calculation.getFocalLength(
                #             picture_coordinates = picture_coordinates,
                #             polar_angle = angle,
                #             distance_target_camera = arm_length + sensor_value
                #         )
                #         focal_length_list.append(new_focal_length)
                #         break
            # focal_length_listがある時はそれを元に移動し確かめる
            else:
                # 今までのfocal_lengthからxy軸との角度を求める
                arm_polar_angle = calculation.getPolarAngleFromFocalLength(
                    picture_coordinates = picture_coordinates,
                    focal_length = sum(focal_length_list)/len(focal_length_list)
                )
                # 移動
                arm.setPolarAngle(polar_angle = arm_polar_angle)
                # センサーの値を取得[mm]
                sensor_value: float = sensor.getValue()
                # 反応した時はそのままfocalLengthに入れる
                if sensor_value <= sensor_threshold:
                    new_focal_length = calculation.getFocalLength(
                            picture_coordinates = picture_coordinates,
                            polar_angle = arm_polar_angle,
                            distance_target_camera = rotation_radius + sensor_value
                        )
                    focal_length_list.append(new_focal_length)
                    break
                # してない時は少し探索する
                else:
                    # TODO focal_length_listを初期化した方がいいか
                    # アームを連続的に動かして焦点距離を特定＆動く
                    new_focal_length = arm.searchFocalLengthContinuously(
                        possible_range = arm_possible_polar_angles,
                        search_range = [arm_polar_angle - SUB_SEARCH_RANGE, arm_polar_angle + SUB_SEARCH_RANGE, ]
                    )
                    # 求めたfocal_lengthを記録
                    focal_length_list.append(new_focal_length)
        else:
            # TODO 初期状態どうする？
            pass

















