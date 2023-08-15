import arm

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
arm = arm.Arm(SERVO_CHANNELS, ARM_LENGTHS)
print(arm.getServoAngles())

arm.setRotationRadius(300)

while True:
    i = int(input('angle: '))
    arm.setPolarAngle(i)
    