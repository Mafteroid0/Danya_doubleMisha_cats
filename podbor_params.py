import math


def shoot_calulating(x: int, y: int, width=250):
    x_okr = width / 2
    y_okr = -300
    radius = math.sqrt((x - x_okr) ** 2 + (y - y_okr) ** 2)

    dx = x - x_okr
    dy = y - y_okr
    anglehorizontal = math.degrees(math.atan(dx / dy))

    return radius, anglehorizontal


# print(shoot(150, 66))
# print(shoot(50, 66))
# print(shoot(250, 250))
