import math
def hex_convert(encoded_color):
    color = bin(encoded_color)[2:]
    r, g, b = int(color[0:7], 2), int(color[8:15], 2), int(color[16::], 2)
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    return hex_color

print(hex_convert(5195743))
print(hex_convert(12052395))
print(hex_convert(3895263))

def distance(color1, color2):
    return math.sqrt(sum([((color1[i]/255) - (color2[i]/255)) ** 2 for i in range(3)]))

