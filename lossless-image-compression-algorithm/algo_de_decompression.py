from PIL import Image
from BaseN import BaseNToDec
from re import split
from math import sqrt,floor
import lzma
import ast
from time import time
def recip_reecriture(entier: int) -> tuple:
    """
    Reciproque de la fonction de Szudzik avec validation des coordonnées
    """
    s = floor(sqrt(entier))
    
    if entier - s*s < s:
        x, y = (entier - s*s, s)
    else:
        x, y = (s, entier - s*s - s)
    # Ajout de logs
    """with open('fichier_log.txt', 'a', encoding="utf-8") as fichier: fichier.write(
        f"Entier reçu: {entier}\n"
        f"s calculé: {s}\n"
        f"Coordonnées calculées: ({x}, {y})\n"
        f"Dimensions image: {width}x{height}\n"
    )"""
    # Validation des coordonnées
    if x < 0 or y < 0 or x >= width or y >= height:
        print(f"Coordonnées invalides générées: ({x}, {y})")
        return None
    return (x, y)

debut=time()
#Etape 1: Ouvrir le fichier xz
with lzma.open("information.txt.xz", "rb") as archive, open("decompressé.txt", "wb") as fichier_txt:
    fichier_txt.write(archive.read())
#Etape 2: placement dans une dictionnaire, Note: Les clés ont le type str
color_positions={}
with open('decompressé.txt', 'r', encoding="ascii") as fichier:
    for ligne in fichier:
        resultat = split(':', ligne)
        resultat[1]=resultat[1].replace('\n','')
        color_positions[resultat[0]]=resultat[1]
(width,height)=(int(color_positions['width,height'].split(",")[0]),int(color_positions['width,height'].split(",")[1]))
#with open("fichier_log.txt", "a",encoding="utf-8") as fichier: fichier.write(f"Dictionnaire des couleurs après reconstruction: {color_positions}\n")
del color_positions['width,height']



#Etape 3: Retour en base 10:
digitset='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"$%&-/;<>=?@[]^_|~'
pattern = f'[{digitset}]+|[*+]'
#Etape 3.1: Phrase en base 10
for color in color_positions.keys():
    result = ''
    current_number = ''
    
    for char in color_positions[color]:
        if char in ('*', '+'):
            if current_number:
                result += BaseNToDec(current_number, digitset)
                current_number = ''
            result += char
        else:
            current_number += char
            
    if current_number:  # Pour le dernier nombre
        result += BaseNToDec(current_number, digitset)
        
    color_positions[color] = result
#Etape 3.2: Reciproque de reecriture et delta
for color in color_positions.keys():
    # Découpage de la chaîne
    nombres = [n for n in color_positions[color].split('+') if n]
    decompresse = []
    
    # Traitement RLE
    for num in nombres:
        if '*' in num:
            try:
                valeur, repetitions = map(int, num.split('*'))
                decompresse.extend([valeur] * repetitions)
            except ValueError as e:
                #with open('fichier_log.txt', 'a', encoding="utf-8") as fichier: fichier.write(f"Erreur RLE: {num}: {e}")
                continue
        else:
            try:
                decompresse.append(int(num))
            except ValueError as e:
                #with open('fichier_log.txt', 'a', encoding="utf-8") as fichier: fichier.write(f"Erreur conversion: {num}: {e}")
                continue
    
    # Décodage delta
    deltas_originaux = decompresse.copy()  # Gardons une copie
    for i in range(1, len(decompresse)):
        decompresse[i] += decompresse[i-1]
    color_positions[color]=decompresse
    
    """with open('fichier_log.txt', 'a', encoding="utf-8") as fichier: fichier.write (
        f"\nTraitement de la couleur: {color}\n"
        f"Après split: {nombres[:10]}\n"
        f"Après RLE: {decompresse[:10]}\n"
        f"Deltas originaux: {deltas_originaux[:10]}\n"
        f"Après décodage: {decompresse[:10]}\n"
        f"{'='*50}\n"
    )"""
        

# Etape 4: Retour dans N^2:
for color in color_positions.keys():
    coordonnees_valides = []
    
    for i in range(len(color_positions[color])):
        valeur = int(color_positions[color][i])
        if valeur < 0:
            #with open('fichier_log.txt', 'a', encoding="utf-8") as fichier: fichier.write(f"Valeur négative détectée: {valeur}")
            continue
            
        coord = recip_reecriture(valeur)
        if coord is not None:
            coordonnees_valides.append(coord)
        """ else:
            with open('fichier_log.txt', 'a', encoding="utf-8") as fichier: fichier.write(f"Échec décodage position {i}")"""
           
            
    color_positions[color] = coordonnees_valides

#Etape 5: Reconstruction de l'image
img = Image.new("RGBA", (width, height), color=(0, 0, 0,0))
color_positions = {ast.literal_eval(k): v for k, v in color_positions.items()}
for color in color_positions.keys():
    for i in range(len(color_positions[color])):
        coord = color_positions[color][i]
        if isinstance(coord, tuple) and len(coord) == 2:
            if 0 <= coord[0] < width and 0 <= coord[1] < height:
                img.putpixel(coord, color)
img.save("final_image.png")

duree=time()-debut
heures = int(duree // 3600)
minutes = int((duree % 3600) // 60)
secondes = int(duree % 60)
with open('fichier_log.txt', 'a', encoding='utf-8') as f:
    f.write(f"Temps écoulé pour la decompression: {heures:02d}h:{minutes:02d}m:{secondes:02d}s\n")
    f.write('-----------------------------------------------------------------------------------------------------------------\n')

"""
r"^\d+\*\d+$": il s'agit d'un schema a detecter 
^ debut de phrase
\d+ plus d'un entier, \d=[0,9] entiers
\*, etoile, le backslash est pour que ce ne soit pas pris comme commande python
$ fin de phrase

"""