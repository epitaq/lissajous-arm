import cv2
import mediapipe as mp
from picamera2 import Picamera2
import copy
import numpy as np

class Camera :
    def __init__ (self):
        # mediapipeの設定
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        # カメラの設定
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        self.picam2.start()

        print('Camera [OK]')

    def calc_palm_moment(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        palm_array = np.empty((0, 2), int)

        for index, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)

            landmark_point = [np.array((landmark_x, landmark_y))]

            # 手首1 手首2 人差指：付け根 中指：付け根 薬指：付け根 小指：付け根
            if index in [0, 1, 5, 9, 13, 17]:
                palm_array = np.append(palm_array, landmark_point, axis=0)

        M = cv2.moments(palm_array)
        cx, cy = 0, 0
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
        # 面積を求める
        s = cv2.contourArea(palm_array) 
        return cx, cy, s

    def getPictureCoordinates(self):
        picture_coordinates = []
        # 撮影
        image = self.picam2.capture_array()
        image_with_circle = copy.deepcopy(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # 画像のサイズ
        image_width, image_height = image.shape[1], image.shape[0]
        # mediapipe
        results = self.hands.process(image)
        # 手の数だけ繰り返し
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                    results.multi_handedness):
                # 手の平重心計算
                cx, cy, s = self.calc_palm_moment(image, hand_landmarks)
                print('cx,cy,s: ',str(cx),str(cy),str(s))
                # 面積が大きい近い｜正面を向いてるから危険性高い
                if picture_coordinates:
                    if picture_coordinates[2] < s:
                        picture_coordinates = [cx-(image_width/2), (image_height/2)-cy, s]
                else:
                    picture_coordinates = [cx-(image_width/2), (image_height/2)-cy, s]
                
                cv2.circle(image_with_circle, (cx, cy), 12, (0, 255, 0), 2)

        # cv2.imshow('MediaPipe Hand Demo', image_with_circle)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return picture_coordinates[:2]

# import camera
# cam = camera.Camera()
# cam.getPictureCoordinates()