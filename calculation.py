import numpy as np

def angleFromRotationRadius (rotation_radius, length_0, length_1):
    angle = arcCos(
        (rotation_radius**2 - length_0**2 - length_1**2)
        / (2 * length_0 * length_1))
    return angle

def azimuthalAngle(x: float, y: float) -> float:
    azimuthal_angle = arcTan(y / x)
    return azimuthal_angle

# なんかおかしい TODO
# ポーラー角の基準と取り方間違えていた
# 90+Θで戻せる
def getFocalLength(picture_coordinates: list[float], polar_angle: float) -> float:
    print('getFocalLength: ',str(picture_coordinates[0]),str(picture_coordinates[1]),str(polar_angle))
    x_2d, y_2d = picture_coordinates
    polar_angle -= 90
    focal_length = np.sqrt((y_2d**2)/(tan(polar_angle)**2) - (x_2d**2))
    # focal_length = np.sqrt(abs(rotation_radius**2 - x_2d**2 - y_2d**2))
    print('  return: ',str(focal_length))
    return focal_length

def getPolarAngleFromFocalLength(picture_coordinates: list[float], focal_length: float) -> float:
    print('getPolarAngleFromFocalLength: ',str(picture_coordinates[0]),str(picture_coordinates[1]),str(focal_length))
    x_2d, y_2d = picture_coordinates
    polar_angle = arcTan((y_2d) / (np.sqrt(x_2d**2 + focal_length**2)))
    # polar_angle = arcSin(y_2d / rotation_radius) 
    polar_angle += 90
    return polar_angle

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