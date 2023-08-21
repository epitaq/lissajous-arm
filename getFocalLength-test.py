import calculation

picture_coordinates=(-100,-171)
polar_angle= int(input(' polar_angle: '))
r = 300

focal_length = calculation.getFocalLength(picture_coordinates, polar_angle)
PolarAngle = calculation.getPolarAngleFromFocalLength(picture_coordinates, focal_length)

# print('focal_length: '+str(focal_length))
# print('PolarAngle : ' + str(PolarAngle))

# ９０度以下の計算がおかしい