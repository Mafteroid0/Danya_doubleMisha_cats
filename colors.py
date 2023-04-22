import math
from typing import Tuple, Any

import itertools

from typing_ import RgbTuple


# class ColorsGroup:
#     def __init__(self, base_color: RgbTuple):
#         self.base = RgbTuple
#
#     def is_similar(self):


def encode_color(encoded_color: int | str) -> RgbTuple:
    if isinstance(encoded_color, str):
        encoded_color = int(encoded_color)
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


def match_colors_combination(
        target_color: RgbTuple,
        available_colors: dict[RgbTuple | str: int],
        weight: int,
        stop_distance: int | float = 0.02
) -> dict[RgbTuple: int] | None:
    if isinstance(list(available_colors.keys())[0], str):
        new_available_colors = {}

        for key, value in available_colors.items():
            new_available_colors[encode_color(key)] = value
        available_colors = new_available_colors

        del new_available_colors

    min_distance = 10
    variant_with_min_distance = None

    for variant in (itertools.product(available_colors, repeat=weight)):
        act_distance = distance(mix_colors(*variant), target_color)

        if act_distance <= stop_distance:
            return variant
        elif act_distance <= min_distance:
            variant_with_min_distance = variant
            min_distance = act_distance

    if variant_with_min_distance is None:
        raise ValueError('Кажется, вы передали пустой available_colors')

    return variant_with_min_distance

# match_colors_combination(
#     (1, 2, 3),
#     {
#         "211851": 2,
#         "211899": 15,
#         "211947": 9,
#         "212807": 9,
#         "212819": 11,
#         "212823": 13,
#         "212903": 12,
#         "212979": 6,
#         "213767": 15,
#         "213867": 11,
#         "213903": 12,
#         "213951": 15,
#         "213959": 11,
#         "214815": 7,
#         "214847": 10,
#         "214855": 11,
#         "214875": 9,
#         "214915": 10
#     },
#     weight=2
# )
