def hex_convert(encoded_color):
    color = bin(encoded_color)[2:]
    r, g, b = int(color[0:7], 2), int(color[8:15], 2), int(color[16::], 2)
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    return hex_color
# print(hex_convert(2032631))