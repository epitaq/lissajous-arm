import numpy as np

def angleFromRotationRadius (rotation_radius, length_0, length_1):
    angle = arcCos(
        (rotation_radius**2 - length_0**2 - length_1**2)
        / (2 * length_0 * length_1))
    return angle

def azimuthalAngle(x: float, y: float) -> float:
    azimuthal_angle = arcTan(y / x)
    return azimuthal_angle

def getFocalLength(picture_coordinates: list[float], polar_angle: float, distance_target_camera: float) -> float:
    return focal_length

def getPolarAngleFromFocalLength(picture_coordinates: list[float], focal_length: float) -> float:
    return polar_angle

# sin cosの計算
def sin (angle):
    return np.sin(np.radians(angle))
def cos (angle):
    return np.cos(np.radians(angle))
def tan (angle):
    return np.tan(np.radians(angle))
def arcSin (x):
    print('arcsin: ' + str(x))
    if x > 1: x = 1
    elif x < -1: x = -1
    return np.degrees(np.arcsin(x))
def arcCos (x):
    print('arccos: ' + str(x))
    if x > 1: x = 1
    elif x < -1: x = -1
    return np.degrees(np.arccos(x))
def arcTan (x):
    print('arctan: '+str(x))
    return np.degrees(np.arctan(x))