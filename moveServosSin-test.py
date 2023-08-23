import arm
import time

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
arm = arm.Arm(SERVO_CHANNELS, ARM_LENGTHS)
print(arm.getServoAngles())
time.sleep(1)
arm.setRotationRadius(
                rotation_radius=300
            )
time.sleep(1)


# angle = int(input('angle: '))
# arm.setPolarAngle(angle)

# arm.searchFocalLengthContinuously(search_range =  [60,120], sensor_threshold= 0)