from PIL import Image
from BaseN import DecToBaseN #Emprunté sur github par harrisonlingren optimisé par chatgpt
from re import findall 
import cv2
import lzma #Pour la compression
import os #Pour avoir la taille des fichiers
import time #Calculs temporels
import numpy as np
#Complexité: O(C+N*Log(N)), C: nombre de couleurs
image_name="images/image_test_7.png"

im = Image.open(image_name)

#Definition de fonctions pour la compression
def reindexation(pixel: tuple) -> int:
    """
    Une bijection entre N^2 et N, on choisit la fonction d'appariement elegante de Szudzik
    """
    if int(pixel[0])<int(pixel[1]): return int(pixel[1])**2+int(pixel[0])
    else: return int(pixel[0])**2+int(pixel[0])+int(pixel[1])

def delta(positions: list) -> list:
    positions.sort()
    for i in range(1,len(positions)):
        positions[-i]-=positions[-(i+1)] #Tjrs positif, normalement......
    for i in range(1,len(positions)):
        positions[i]="+" + str(positions[i])
    return positions

def reecriture(positions:list)->str:
    """On veut faire une phrase qui prendra moins d'espace dans le fichier txt et qui sera facile a decoder, illustration de l'algo:
    [100,105,108,111,120,155,190,225]--delta-->[100,'+5','+3','+3','+12','+35','+35','+35']--reecriture-->'100+5+3*2+12+35*3' Dans la version optimisée on utilise la méthode des deux pointeurs O(n^2)->O(n)"""
    left, right = 0, 1
    phrase_fractionnee = []

    while right < len(positions):
        if positions[right] == positions[left]:
            right += 1
        else:
            if right - left == 1:
                phrase_fractionnee.append(str(positions[left]))
            else:
                phrase_fractionnee.append(f'{positions[left]}*{right-left}')
            left = right
            right += 1
    # dernier bloc
    if right - left == 1:
        phrase_fractionnee.append(str(positions[left]))
    else:
        phrase_fractionnee.append(f'{positions[left]}*{right-left}')

    return ''.join(phrase_fractionnee)

temps_de_depart=time.time()
(width, height) = im.size
# Collecte des couleurs existantes et association des pixels 
color_positions = {}
for x in range(width):
    for y in range(height):
        pixel_color = im.getpixel((x, y))
        if pixel_color not in color_positions:
            color_positions[pixel_color]=[]
            color_positions[pixel_color].append((x, y))
        else: color_positions[pixel_color].append((x, y))



#Reduction du dictionnaire, pt1: On applique delta et reecriture
for color in color_positions.keys():
    positions = [reindexation(tuple(coord)) for coord in color_positions[color]]
    positions = delta(positions)
    color_positions[color] = reecriture(positions)
#Reduction du dictionnaire, pt2: On va passer en une base de numerotation supérieure, a l'aide de la fonction DecToBaseN, il s'agit d'une bijection entre N  et digiset qui est une partie de l'ensemble des caractères ascii
digitset='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"$%&-/;<>=?@[]^_|~'
for color in color_positions.keys():
    temp_list=findall(r"\d+|[*+]",color_positions[color])
    for i in range(len(temp_list)):
        if temp_list[i].isdigit(): temp_list[i]=DecToBaseN(int(temp_list[i]), digitset)
    color_positions[color]=''.join(temp_list)

# Écriture des informations dans le fichier
with open('information.txt', 'w', encoding="ascii") as fichier:
    for color, positions in color_positions.items(): fichier.write(f"{color}:{positions}\n")
    fichier.write(f"width,height:{width},{height}")

#Compression en .xz
with open("information.txt", "rb") as information, lzma.open("information.txt.xz", "wb", preset=9) as compressé:
    compressé.write(information.read())
taille_originale=os.path.getsize(image_name)
taille_compressée=os.path.getsize("information.txt.xz")


#Compte rendu dans le fichier log
duree=time.time()-temps_de_depart
heures = int(duree // 3600)
minutes = int((duree % 3600) // 60)
secondes = int(duree % 60)
with open('fichier_log.txt','a',encoding='utf-8') as f:
    f.write(f"\nResultats pour: {image_name}\n")
    f.write(f"Dimensions:{width}x{height}\n")
    f.write(f"Temps écoulé pour la compression: {heures:02d}h:{minutes:02d}m:{secondes:02d}s\n")
if taille_compressée>=taille_originale: 
    with open('fichier_log.txt','a',encoding='utf-8') as f: f.write(f"Echec | ")
else:
    with open('fichier_log.txt','a',encoding='utf-8') as f: f.write(f"Succès | ")
with open('fichier_log.txt','a',encoding='utf-8') as f: f.write(f"Taille originale/Taille compressée:{taille_originale}/{taille_compressée}\n")



