# x = base 10 [str], d = set of ordered unique 'digits' [str]
def DecToBaseN(x, d):
    """Convertit un entier décimal (str) en base len(d)"""
    k = int(x)
    n = len(d)
    if k < n:
        return d[k]

    b = []
    while k > 0:
        r = k % n
        b.append(d[r])   # on stocke dans une liste (append O(1))
        k //= n

    return ''.join(reversed(b))  # join O(L), beaucoup plus rapide que concat répétée


# x = base N number as [str], d = set of ordered unique 'digits' [str]
def BaseNToDec(x, d):
    """Convertit un nombre en base len(d) (str) en décimal (str)"""
    m = len(d)
    # création d'un dictionnaire pour lookup rapide O(1)
    d_map = {symbol: i for i, symbol in enumerate(d)}

    b = 0
    for char in x:
        b = b * m + d_map[char]  # formule classique de conversion
    return str(b)

