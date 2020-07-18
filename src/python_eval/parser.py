import sys
from PIL import Image
import os
sys.setrecursionlimit(1000000)

with open('src/mfs/messages/galaxy.txt', 'rt') as f:
    lines = [line.strip().split(' ') for line in f]

def eager(x, deep=False):
    if isinstance(x, F):
        x = x.eager()
    if deep and isinstance(x, F):
        x.args = tuple(eager(arg, deep=True) for arg in x.args)
    return x

class F:
    def __init__(self, name, arity, apply, args=()):
        self.name = name
        self.arity = arity
        self.args = args
        self.apply = apply
    
    def __call__(self, *new_args):
        if self.arity == 0:
            return self.eager()(*new_args)
        if self.arity >= len(new_args):
            return F(self.name, self.arity - len(new_args), self.apply, self.args + new_args)
        else:
            f = self.apply(*(self.args + new_args[:self.arity]))
            return f(*new_args[self.arity:])
    
    def __repr__(self):
        if not self.args:
            return self.name
        return f"({self.name} {' '.join(str(arg) for arg in self.args)})"
    
    def eager(self):
        if hasattr(self, 'cache'):
            return self.cache
        if self.arity == 0:
            self.cache = eager(self.apply(*self.args))
            return self.cache
        return self

def cons_f(x, xs, f):
    return f(x, xs)

def code(val, append_to=None):
    if append_to is None:
        ar = []
        code(val, ar)
        return ' '.join(ar)
    if isinstance(val, F):
        for i in range(len(val.args)):
            append_to.append('ap')
        append_to.append(val.name)
        for arg in val.args:
            code(arg, append_to)
    else:
        append_to.append(str(val))

true = F('t', 2, lambda x, y: x)
false = F('f', 2, lambda x, y: y)

nil = F('nil', 1, lambda x: true)
cons = F('cons', 3, cons_f)
vec = F('vec', 3, cons_f)
car = F('car', 1, lambda lst: lst(true))
cdr = F('cdr', 1, lambda lst: lst(false))

def quot(a, b):
    return a//b if a*b>0 else (a+(-a%b))//b

assert quot(4, 2) == 2
assert quot(4, 3) == 1
assert quot(4, 4) == 1
assert quot(4, 5) == 0
assert quot(5, 2) == 2
assert quot(6, -2) == -3
assert quot(5, -3) == -1
assert quot(-5, 3) == -1
assert quot(-5, -3) == 1

def _isnil(lst):
    assert isinstance(lst, F) and lst.name in ('nil', 'cons', 'vec'), f'{lst} is not valid argument for isnil'
    return true if lst.name == 'nil' else false

toplevel = {
    't': true,
    'f': false,
    'nil': nil,
    'cons': cons,
    'vec': vec,
    'car': car,
    'cdr': cdr,
    'neg': F('neg', 1, lambda x: -eager(x)),
    'add': F('add', 2, lambda x, y: eager(x) + eager(y)),
    'mul': F('mul', 2, lambda x, y: eager(x) * eager(y)),
    'eq': F('eq', 2, lambda x, y: true if eager(x) == eager(y) else false),
    'lt': F('lt', 2, lambda x, y: true if eager(x) < eager(y) else false),
    's': F('s', 3, lambda x, y, z: x(z, y(z))),
    'c': F('c', 3, lambda x, y, z: x(z, y)),
    'b': F('b', 3, lambda x, y, z: x(y(z))),
    'i': F('i', 1, lambda x: x),
    'div': F('div', 2, lambda a, b: quot(eager(a), eager(b))),
    'isnil': F('isnil', 1, lambda lst: _isnil(eager(lst))),
}

symbols = {}
def capture(expr):
    return lambda: eval(expr)
for line in lines:
    symbols[line[0]] = F('&' + line[0], 0, capture(line[2:]))

def eval(expr):
    ip = 0
    def _eval():
        nonlocal ip
        op = expr[ip]
        ip += 1
        if op == 'ap':
            f = _eval()
            x = _eval()
            return f(x)
        elif op in toplevel:
            return toplevel[op]
        elif op in symbols:
            return symbols[op]
        else:
            return int(op)
    return _eval()

def to_python(val):
    val = eager(val)
    if isinstance(val, F):
        if val.name == 'cons':
            assert len(val.args) == 2
            head = to_python(val.args[0])
            tail = to_python(val.args[1])
            if not isinstance(tail, list):
                tail = [tail]
            return [head] + tail
        elif val.name == 'nil':
            return []
        elif val.name == 'vec':
            assert len(val.args) == 2
            a = to_python(val.args[0])
            b = to_python(val.args[1])
            return (a, b)
        else:
            assert False
    else:
        return val


def from_python(x):
    if type(x) == list:
        if len(x) == 0:
            return nil
        else:
            return cons(from_python(x[0]), from_python(x[1:]))
    else:
        assert type(x) == int, x
        return x

# print(eager(symbols[':1128'](cons(10, cons(10, cons(10, nil)))), deep=True))
# print(eager(symbols['galaxy'](cons(0, nil), vec(0, 0)), deep=True))

def draw(points, out, color=(255, 255, 255)):
    if not points:
        print(f'empty points for {out}')
        return
    minx, miny = -160, -160
    maxx, maxy = 160, 160
    # minx, miny = points[0]
    # maxx, maxy = points[0]
    for x, y in points:
        minx = min(minx, x)
        maxx = max(maxx, x)
        miny = min(miny, y)
        maxy = max(maxy, y)
    im = Image.new("RGB", (maxx - minx + 1, maxy - miny + 1), 'black')
    pixels = im.load()
    for x, y in points:
        pixels[x - minx, y - miny] = color
    im.save(out)

override_vec = {
    3: vec(8, 4),
    4: vec(2, -8),
    5: vec(3, 6),
    6: vec(0, -14),
    7: vec(-4, 10),
    8: vec(9, -3),
    9: vec(-4, 10),
    10: vec(1, 4),
}

state = cons(1, cons(cons(1, nil), cons(0, cons(nil, nil))))
# state = cons(2, cons(cons(1, cons(-1, nil)), cons(0, cons(nil, nil))))
for iter in range(12):
    os.makedirs(f'{iter}', exist_ok=True)
    coords = vec(0, 0)
    if iter in override_vec:
        coords = override_vec[iter]
    it = symbols['galaxy'](state, coords)
    state = eager(car(cdr(it)), deep=True)
    flag, st, data = to_python(it)
    print(flag, st, data)
    for i, imgData in enumerate(data):
        fn = f'{iter}/{i}.png'
        draw(imgData, fn)
