import numpy as np

def angleFromRotationRadius (rotation_radius, length_0, length_1):
    angle = arcCos(
        (rotation_radius**2 - length_0**2 - length_1**2)
        / (2 * length_0 * length_1))
    return angle

def azimuthalAngle(x: float, y: float) -> float:
    # azimuthal_angle = arcTan(y / x)
    azimuthal_angle = np.degrees(np.arctan2(y, x))
    if azimuthal_angle < 0: 
        azimuthal_angle += 180
    return azimuthal_angle

# 第何象限にあるかで角度はきまるはず
def getFocalLength(picture_coordinates: list[float], polar_angle: float) -> float:
    print('getFocalLength: ',str(picture_coordinates[0]),str(picture_coordinates[1]),str(polar_angle))
    x, y = picture_coordinates
    focal_length = np.sqrt(x**2 + y**2) * tan(polar_angle)
    if y < 0:
        focal_length *= -1
    print('  return: ',str(focal_length))
    # 計算上ありえないと思うが負の値だとアームが壊れるから絶対値をつける
    if focal_length < 0:
        print('[FAILED] focal_length is minus')
    return abs(focal_length)

def getPolarAngleFromFocalLength(picture_coordinates: list[float], focal_length: float) -> float:
    print('getPolarAngleFromFocalLength: ',str(picture_coordinates[0]),str(picture_coordinates[1]),str(focal_length))
    x, y = picture_coordinates
    polar_angle = np.degrees(np.arctan2(focal_length, np.sqrt(x**2 + y**2) ))
    if y < 0:
        polar_angle = 180 - polar_angle
    print('    return: ',str(polar_angle))
    # 2
    if polar_angle < 0:
        print('[FAILED] polar_angle is minus')
    return abs(polar_angle)

def getStep(angle):
    '''
        sinを使った制御用の速度調節用
    '''
    angle = abs(angle)
    if angle > 100: return 1
    elif 100 >= angle > 45: return 3
    elif 45 >= angle > 20: return 5
    elif 20 >= angle >= 10: return 20
    elif 10 > angle : return -1

# sin cosの計算
def sin (angle):
    return np.sin(np.radians(angle))
def cos (angle):
    return np.cos(np.radians(angle))
def tan (angle):
    return np.tan(np.radians(angle))
def arcSin (x):
    # print('arcsin: ' + str(x))
    if x > 1: x = 1
    elif x < -1: x = -1
    return np.degrees(np.arcsin(x))
def arcCos (x):
    # print('arccos: ' + str(x))
    if x > 1: x = 1
    elif x < -1: x = -1
    return np.degrees(np.arccos(x))
def arcTan (x):
    # print('arctan: '+str(x))
    return np.degrees(np.arctan(x))