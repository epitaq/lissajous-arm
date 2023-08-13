import arm

SERVO_CHANNELS = {'root_servo': 0,'head_servo': 1,'root_head_servo': 2,'root_link_servo': 3}
ARM_LENGTHS = {'head_arm_length': 120,'root_head_arm_length': 100,'root_link_arm_length': 30}
arm = arm.Arm(SERVO_CHANNELS, ARM_LENGTHS)
print(arm.getServoAngles())
arm.moveServos(angles= {
    'root_servo': 30,
    'head_servo':20,
    'root_head_servo': 5,
    'root_link_servo': 30})
print(arm.getServoAngles())
