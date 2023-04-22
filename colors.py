import functools
import math
from typing import Any

import itertools

from typing_ import RgbTuple


class VariantNotFoundError(Exception):
    pass


class ColorsGroup:
    def __init__(self, base_color: RgbTuple, max_distance: int | float = 0.02):
        self._base_color = base_color
        self.max_distance = max_distance
        self.mine_colors = {}

    @property
    def base_color(self):
        return self._base_color

    @classmethod
    def multy_from_dict(cls, colors: dict[RgbTuple | str, int], max_distance: int | float = 0.02):
        if isinstance(list(colors.keys())[0], str):
            new_colors = {}

            for key, value in colors.items():
                new_colors[encode_color(key)] = value
            colors = new_colors

            del new_colors

        groups = set()

        while colors:
            group = cls(next(iter(colors)))
            groups.add(group)

            colors = group.get_mine(colors)

        return groups

    @functools.cache
    def is_mine(self, color: RgbTuple) -> bool:
        return distance(self.base_color, color) <= self.max_distance

    def get_mine(self, colors: dict[RgbTuple, int]) -> dict[RgbTuple, int]:
        remainders = {}
        for color, amount in colors.items():
            if self.is_mine(color):
                self.mine_colors[color] = amount
            else:
                remainders[color] = amount

        del colors

        self.mine_colors = {
            key: self.mine_colors[key]
            for key in sorted(self.mine_colors, key=lambda color: distance(color, self.base_color))
        }

        return remainders

    def get_colors(self, limit: int, mult: bool = True) -> list[RgbTuple]:
        res = []

        for color, amount in self.mine_colors.items():
            if len(res) >= limit:
                break

            if amount == 0:
                continue

            if not mult:
                amount = 1

            res += [color] * amount

        return res

    def __repr__(self):
        return f'ColorsGroup({self.base_color})'


def decode_color(encoded_color: int | str) -> RgbTuple:
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
        rgb = decode_color(int(color))  # получили ргб

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
        available_colors: dict[ColorsGroup | str: int],
        weight: int,
        stop_distance: int | float = 0.02,
        critical_distance: int | float = 0.5
) -> dict[RgbTuple: int] | None:
    if isinstance(list(available_colors.keys())[0], str):
        new_available_colors = {}

        for key, value in available_colors.items():
            new_available_colors[decode_color(key)] = value
        available_colors = new_available_colors

        del new_available_colors

    min_distance = 10
    variant_with_min_distance = None

    if target_color in available_colors.keys():
        return target_color,

    for variant in (itertools.product(filter(lambda color: available_colors[color] >= weight, available_colors), repeat=weight)):
        act_distance = distance(mix_colors(*variant), target_color)

        if act_distance <= stop_distance:
            return encode_color(variant)
        elif act_distance <= min_distance:
            variant_with_min_distance = variant
            min_distance = act_distance

    if variant_with_min_distance is None:
        raise ValueError('Кажется, вы передали пустой available_colors')

    if min_distance >= critical_distance:
        raise VariantNotFoundError()

    return encode_color(variant_with_min_distance)


def encode_color(rgb):
    d = list(rgb[0])
    return ((d[0] << 16) + (d[1] << 8) + d[2])  # r g b
