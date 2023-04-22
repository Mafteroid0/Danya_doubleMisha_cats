import math
from typing import Tuple, Any

from typing_ import RgbTuple


def encode_color(encoded_color) -> RgbTuple:
    color = bin(encoded_color)[2:]
    rgb = (int(color[0:7], 2), int(color[8:15], 2), int(color[16::], 2))
    return rgb


def mix_colors(*args: RgbTuple) -> RgbTuple | tuple[int | Any, ...]:
    return tuple([sum(map(lambda color: color[i], args)) // len(args) for i in range(3)])


def distance(color1: RgbTuple, color2: RgbTuple):
    return math.sqrt(sum([((color1[i] / 255) - (color2[i] / 255)) ** 2 for i in range(3)]))


def closest_color(json_list) -> tuple[RgbTuple, RgbTuple]:
    red = (194, 39, 45)
    black = (36, 36, 36)

    lowest_distance_red = lowest_distance_black = 5000

    closest_black_color = ""  # запоминаем цвета
    closest_red_color = ""

    for color in json_list:  # 24bit color
        rgb = encode_color(int(color))  # получили ргб

        red_difference = distance(red, rgb)
        black_difference = distance(black, rgb)

        if red_difference < lowest_distance_red:
            lowest_distance_red = red_difference
            closest_red_color = color

        if black_difference < lowest_distance_black:
            lowest_distance_black = black_difference
            closest_black_color = color

    return closest_red_color, closest_black_color


# def choice_
