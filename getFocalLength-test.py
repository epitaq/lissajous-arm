import calculation

picture_coordinates=(0,400)
polar_angle= int(input(' polar_angle: '))

focal_length = calculation.getFocalLength(picture_coordinates, polar_angle, 0)
PolarAngle = calculation.getPolarAngleFromFocalLength(picture_coordinates, focal_length)

print('focal_length: '+str(focal_length))
print('PolarAngle : ' + str(PolarAngle))