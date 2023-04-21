import math


def encode_color(encoded_color):
    color = bin(encoded_color)[2:]
    rgb = tuple([int(color[0:7], 2), int(color[8:15], 2), int(color[16::], 2)])
    return rgb


def distance(color1, color2):
    return math.sqrt(sum([((color1[i] / 255) - (color2[i] / 255)) ** 2 for i in range(3)]))


def closest_color(json_list):
    red = tuple([194, 39, 45])
    black = tuple([36, 36, 36])

    lowest_distance_red = 5000
    lowest_distance_black = 5000
    lowest_black_color = ""  # запоминаем цвета
    lowest_red_color = ""
    for color in json_list:  # 24bit color
        rgb = encode_color(int(color))  # получили ргб
        red_difference = distance(red, rgb)
        black_difference = distance(black, rgb)
        if red_difference < lowest_distance_red: lowest_distance_red = red_difference; lowest_red_color = color
        if black_difference < lowest_distance_black: lowest_distance_black = black_difference; lowest_black_color = color

    return (lowest_red_color, lowest_black_color)
