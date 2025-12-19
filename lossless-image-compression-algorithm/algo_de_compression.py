from PIL import Image
from BaseN import DecToBaseN 
from re import findall 
import lzma

image_name = "path_to_image" # Replace path_to_image by the path to the image
im = Image.open(image_name)

def pairing_function(pixel: tuple) -> int:
    """
    A bijection between N^2 and N. We choose Szudzik's elegant pairing function.
    """
    if int(pixel[0]) < int(pixel[1]): 
        return int(pixel[1])**2 + int(pixel[0])
    else: 
        return int(pixel[0])**2 + int(pixel[0]) + int(pixel[1])

def delta_encode(positions: list) -> list:
    """
    Implementation of differential encoding.
    """
    for i in range(len(positions)):
        positions[i] = pairing_function(positions[i])
    positions.sort()
    
    # Calculate differences (iterate backwards)
    for i in range(1, len(positions)):
        positions[-i] -= positions[-(i+1)] 
    
    # Add '+' prefix to indicate a positive difference
    for i in range(1, len(positions)):
        positions[i] = "+" + str(positions[i])
    return positions

def rewrite(positions: list) -> str:
    """
    The goal is to create a string that takes up less space in the txt file 
    and is easy to decode.
    Algorithm illustration :
 [100 ,105 ,108 ,111 ,120 ,155 ,190 ,225] -- delta_encode - - > [100 , ’+5 ’ , ’+3 ’ , ’+3 ’ , ’+12 ’ , ’+35 ’ , ’+35 ’ , ’+35 ’]
 -- rewrite - - > ’100+5+3*2+12+35*3 ’

    """
    left, right = 0, 1
    split_phrase = []

    while right < len(positions):
        if positions[right] == positions[left]:
            right += 1
        else:
            if right - left == 1:
                split_phrase.append(str(positions[left]))
            else:
                split_phrase.append(f'{positions[left]}*{right-left}')
            left = right
            right += 1
    # Process the last block
    if right - left == 1:
        split_phrase.append(str(positions[left]))
    else:
        split_phrase.append(f'{positions[left]}*{right-left}')
    return ''.join(split_phrase)

# Dictionary Creation {color: list_of_coordinates}
(width, height) = im.size
color_positions = {}
for x in range(width):
    for y in range(height):
        pixel_color = im.getpixel((x, y))
        if pixel_color not in color_positions:
            color_positions[pixel_color] = []
            color_positions[pixel_color].append((x, y))
        else: 
            color_positions[pixel_color].append((x, y))

# Dictionary Reduction
for color in color_positions.keys():
    color_positions[color] = rewrite(delta_encode(color_positions[color]))

digitset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"$%&-/;<>=?@[]^_|~'
for color in color_positions.keys():
    temp_list = findall(r"\d+|[*+]", color_positions[color])
    for i in range(len(temp_list)):
        if temp_list[i].isdigit(): 
            temp_list[i] = DecToBaseN(int(temp_list[i]), digitset)
    color_positions[color] = ''.join(temp_list)

# Writing information to the .txt file
# We add dimensions for reconstruction
with open('information.txt', 'w', encoding="ascii") as file:
    for color, positions in color_positions.items(): 
        file.write(f"{color}:{positions}\n")
    file.write(f"width,height:{width},{height}")

# Compression to .xz
with open("information.txt", "rb") as info_file, lzma.open("information.txt.xz", "wb", preset=9) as compressed_file:
    compressed_file.write(info_file.read())
