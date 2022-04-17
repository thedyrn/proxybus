def hTa(_hex):
    if _hex > 9:
        _hex += 7
    return _hex + 48


def bTh(n, length=2, add=0):
    n += add
    n1 = n % 16
    n = n // 16
    n2 = n % 16
    n = n // 16
    n3 = n % 16
    n = n // 16
    return [hTa(n), hTa(n3), hTa(n2), hTa(n1)][4 - length:]


def sumCheck(_list):
    out = 0
    for i in _list[1:]:
        out += i
    return bTh(out)


def sumCheckBytes(_bytes):
    out = 0
    for i in _bytes[1:-2]:
        out += i
    return bTh(out)