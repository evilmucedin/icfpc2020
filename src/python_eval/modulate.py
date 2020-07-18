_REPR = [
  [0, 0, 0, 0], # 0
  [1, 0, 0, 0], # 1
  [0, 1, 0, 0], # 2
  [1, 1, 0, 0], # 3
  [0, 0, 1, 0], # 4
  [1, 0, 1, 0], # 5
  [0, 1, 1, 0], # 6
  [1, 1, 1, 0], # 7
  [0, 0, 0, 1], # 8
  [1, 0, 0, 1], # 9
  [0, 1, 0, 1], # 10
  [1, 1, 0, 1], # 11
  [0, 0, 1, 1], # 12
  [1, 0, 1, 1], # 13
  [0, 1, 1, 1], # 14
  [1, 1, 1, 1], # 15
]

def _modulate_number_no_sign(x):
    if x == 0: return [0]
    if x < 0: x = -x
    n = 0
    res = []
    while x > 0:
        res.extend(_REPR[x % 16])
        x = x // 16
        n += 1
    res.append(0)
    res.reverse()
    return [1] * n + res

def modulate_number(n):
    return ([0, 1] if n >= 0 else [1, 0]) + _modulate_number_no_sign(n)

def modulate_nil():
    return [0, 0]

# Distinguishes between lists and tuples!!! [a, b] <=> (a, (b, nil)), tuple (a, b) <=> (a, b), tuples only of 2 elements allowed
def modulate_anything(x):
    if type(x) == list:
        # list is a pair (x[0], x[1:]) or nil if empty
        res = []
        for v in x:
            res.extend([1, 1])
            res.extend(modulate_anything(v))
        res.extend([0, 0])
        return res
    if type(x) == tuple:
        assert len(x) == 2, x
        res = [1, 1]
        res.extend(modulate_anything(x[0]))
        res.extend(modulate_anything(x[1]))
        return res
    assert type(x) == int, x
    return modulate_number(x)

def to_str(modulation):
    return ''.join(map(str, modulation))

assert to_str(modulate_anything(0)) == '010'
assert to_str(modulate_anything(1)) == '01100001'
assert to_str(modulate_anything(-1)) == '10100001'
assert to_str(modulate_anything((1, 2))) == '110110000101100010'
assert to_str(modulate_anything([1, (2, 3), 4])) == '110110000111110110001001100011110110010000'
assert to_str(modulate_anything([1, [2, 3], 4])) == '1101100001111101100010110110001100110110010000'


# demodulation input is a string + coordinate to start read from, output is value + position of reading
def _demodulate_number_no_sign(val, ind):
    ones = 0
    while val[ind] == '1':
        ind += 1
        ones += 1
    ind += 1 # skip '0'
    if ones == 0:
        return 0, ind
    end = ind + 4 * ones
    assert len(val) >= end
    n = val[ind:end]
    ind = end
    return int(n, 2), ind

# demodulation input is a string + coordinate to start read from, output is value + position of reading
def _demodulate_number(val, ind):
    start = val[ind:(ind+2)]
    if start == '01':
        sgn = 1
    elif start == '10':
        sgn = -1
    else:
        assert False, "Wrong number format"
    ind += 2
    n, ind = _demodulate_number_no_sign(val, ind)
    return sgn * n, ind

def _demodulate_anything(val, ind):
    prefix = val[ind:ind+2]
    assert len(prefix) == 2
    ind += 2
    if prefix == '00':
        return [], ind
    elif prefix == '11':
        # Can be list or a pair
        res = []
        while True:
            elem, ind = _demodulate_anything(val, ind)
            res.append(elem)
            assert ind+2 <= len(val)
            p = val[ind: ind+2]
            ind += 2
            if p == '00':
                return res, ind
            elif p == '11':
                continue
            else:
                # not a list - not ending in a nil
                ind -= 2 # retract
                n, ind = _demodulate_number(val, ind)
                ret = n
                while len(res) > 0:
                    ret = (res.pop(), ret)
                return ret, ind
    else:
        ind -= 2
        return _demodulate_number(val, ind)

def demodulate(val):
    return _demodulate_anything(val, 0)[0]


assert to_str(modulate_anything(demodulate('010'))) == '010'
assert to_str(modulate_anything(demodulate('01100011'))) == '01100011'
assert to_str(modulate_anything(demodulate('110110000101100010'))) == '110110000101100010'
assert to_str(modulate_anything(demodulate('110110000111110110001001100011110110010000'))) == '110110000111110110001001100011110110010000'
assert to_str(modulate_anything(demodulate('1101100001111101100010110110001100110110010000'))) == '1101100001111101100010110110001100110110010000'

#print(demodulate('110110000111110110001001100011110110010000'))
#print(demodulate('1101100001111101100010110110001100110110010000'))


