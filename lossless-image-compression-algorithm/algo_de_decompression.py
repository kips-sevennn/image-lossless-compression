from PIL import Image
from BaseN import BaseNToDec
from math import sqrt, floor
import lzma

def inverse_pairing(integer: int) -> tuple:
    """
    The reciprocal of the elegant pairing function (Szudzik's unpairing).
    Retrieves (x, y) coordinates from the integer z.
    """
    s = floor(sqrt(integer))
    if integer - s*s < s: 
        (x, y) = (integer - s*s, s)
    else: 
        (x, y) = (s, integer - s*s - s)
    return (x, y)

# 1. Read the archive and recreate the dictionary
# Extract the .xz archive to a temporary text file
with lzma.open("information.txt.xz", "rb") as archive, open("decompressed.txt", "wb") as txt_file: 
    txt_file.write(archive.read())

color_positions = {}
with open('decompressed.txt', 'r', encoding="ascii") as file:
    for line in file:
        result = line.split(':')
        result[1] = result[1].replace('\n','') # Remove newline char
        color_positions[result[0]] = result[1]

# Extract dimensions and remove them from the dictionary to avoid processing errors
# Note: The key 'width,height' was added during compression
(width, height) = (int(color_positions['width,height'].split(",")[0]), int(color_positions['width,height'].split(",")[1]))
del color_positions['width,height']

# 2. Decode Base 77 -> Base 10
digitset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"$%&-/;<>=?@[]^_|~'

for color in color_positions.keys():
    result = ''
    current_number = ''
    
    for char in color_positions[color]:
        if char in ('*', '+'):
            # If we hit a separator, decode the number we just built
            if current_number:
                result += BaseNToDec(current_number, digitset)
                current_number = ''
            result += char
        else:
            current_number += char
            
    if current_number:  # Process the last number if exists
        result += BaseNToDec(current_number, digitset)
        
    color_positions[color] = result

# 3. Reconstruct the list and Delta Decode
for color in color_positions.keys():
    # Split string by '+'
    numbers = [n for n in color_positions[color].split('+') if n] 
    decompressed_list = []
    
    # Reconstruct the list of integers, handling '*' run-length encoding
    for num in numbers:
        if '*' in num:
            value, repetitions = map(int, num.split('*')) 
            decompressed_list.extend([value] * repetitions)
        else:
            decompressed_list.append(int(num))
            
    # Delta decoding (cumulative sum)
    for i in range(1, len(decompressed_list)):
        decompressed_list[i] += decompressed_list[i-1]
    color_positions[color] = decompressed_list

# 4. Return to 2D coordinates (Inverse Pairing)
for color in color_positions.keys():
    pixel_coords = []
    for i in range(len(color_positions[color])):
        val = int(color_positions[color][i])     
        pixel_coords.append(inverse_pairing(val))
    color_positions[color] = pixel_coords

# 5. Reconstruct the Image
img = Image.new("RGBA", (width, height), color=(0,0,0,0))
# Convert string representation of tuple keys back to actual tuples (e.g., "(255, 0, 0)")
color_positions = {eval(k): v for k, v in color_positions.items()}

for color in color_positions.keys():
    for i in range(len(color_positions[color])):
        coord = color_positions[color][i]
        img.putpixel(coord, color)

output_filename = "final_image.png"
img.save(output_filename)
