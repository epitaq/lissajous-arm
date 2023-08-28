import arm

SERVO_CHANNELS = {
    'root_servo': 0,
    'head_servo': 4,
    'root_head_servo': 8,
    'root_link_servo': 12
}
ARM_LENGTHS = {
    'head_arm_length': 120,
    'root_head_arm_length': 200,
    'root_link_arm_length': 50
}
arm = arm.Arm(SERVO_CHANNELS, ARM_LENGTHS)
print(arm.getServoAngles())
# arm.setRotationRadius(200)