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

while True:
    angle = int(input('root_head_servo: '))
    angle1 = int(input('root_link_servo: '))
    arm.moveServos(angles= {
        'root_servo': 30,
        'head_servo':20,
        'root_head_servo': angle,
        'root_link_servo': angle1})
    print(arm.getServoAngles())
# arm.moveServos(angles= {'root_servo': 30,'head_servo':20,'root_head_servo': 5,'root_link_servo': 0})