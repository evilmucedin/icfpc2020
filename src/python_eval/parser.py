import pprint
import sys
from PIL import Image, ImageTk
from interaction import send
import os
import tkinter as tk
sys.setrecursionlimit(1000000)

HALF_WIDTH, HALF_HEIGHT = 196, 196
COLORS = [(255, 255, 255), (196, 196, 196), (128, 128, 128), (64, 64, 64), (32, 32, 32), (16, 16, 16), (8, 8, 8), (4, 4, 4), (2, 2, 2)]
SCALE_FACTOR = 3

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
        lines = ['(' + self.name]
        for arg in self.args:
            lines.extend(' ' + line for line in repr(arg).split('\n'))
        lines[-1] = lines[-1] + ')'
        return '\n'.join(lines)
    
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
    'inc': F('inc', 1, lambda x: eager(x) + 1),
    'dec': F('dec', 1, lambda x: eager(x) - 1),
    'neg': F('neg', 1, lambda x: -eager(x)),
    'add': F('add', 2, lambda x, y: eager(x) + eager(y)),
    'mul': F('mul', 2, lambda x, y: eager(x) * eager(y)),
    'eq': F('eq', 2, lambda x, y: true if eager(x) == eager(y) else false),
    'lt': F('lt', 2, lambda x, y: true if eager(x) < eager(y) else false),
    's': F('s', 3, lambda x, y, z: x(z, F('lazy_ap', 0, lambda: y(z)))),
    'c': F('c', 3, lambda x, y, z: x(z, y)),
    'b': F('b', 3, lambda x, y, z: x(F('lazy_ap', 0, lambda: y(z)))),
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
    elif type(x) == tuple:
        assert len(x) == 2, x
        return vec(from_python(x[0]), from_python(x[1]))
    else:
        assert type(x) == int, x
        return x

def drawState(state, in_data):
    while True:
        raw_result = symbols['galaxy'](state, in_data)
        flag, st, data = to_python(raw_result)
        state = eager(car(cdr(raw_result)), deep=True)
        if flag == 0:
            break
        else:
            in_data = from_python(send(data))
    im = Image.new("RGB", (2 * HALF_WIDTH + 1, 2 * HALF_HEIGHT + 1), 'black')
    pixels = im.load()
    for ci, points in reversed(list(enumerate(data))):
        for x, y in points:
            # assert -HALF_WIDTH <= x <= HALF_WIDTH
            # assert -HALF_HEIGHT <= y <= HALF_HEIGHT
            pixels[x + HALF_WIDTH, y + HALF_HEIGHT] = COLORS[ci]
    return state, im

if __name__ == "__main__":
    root = tk.Tk()

    def on_click(event):
        process_click(event.x // SCALE_FACTOR - HALF_WIDTH, event.y // SCALE_FACTOR - HALF_HEIGHT)

    w = tk.Canvas(root, width=SCALE_FACTOR * (2 * HALF_WIDTH + 1), height=SCALE_FACTOR * (2 * HALF_HEIGHT + 1))
    w.bind("<Button-1>", on_click)
    w.pack()

    # state = nil
    # state = cons(1, cons(cons(1, nil), cons(0, cons(nil, nil))))
    # state = cons(2, cons(cons(1, cons(-1, nil)), cons(0, cons(nil, nil))))
    state = from_python([5, [2, 0, [], [], [], [], [], 44309], 9, []])
    # state = from_python([5, [4, 8734024551968111442, [], [], [], [], (36, 0), 44309], 9, []])
    # state = from_python([6, [5, 8, 6725791729228031769, 0, 11, 0, [], [], 4, [0, [], [[[1, 1, (16, 86), (0, 0), [32, 0, 0, 1], 0, 64, 1], []], [[0, 0, (0, 16), (0, 0), [6, 0, 4, 1], 60, 64, 1], []]]], [16, 0, [512, 1, 64], [], []], [], []], 8, []])

    def process_click(x, y):
        global state, img
        print(f'click at {x}:{y} at state\n{pprint.pformat(to_python(state))}')
        state, img = drawState(state, vec(x, y))
        img = img.resize((SCALE_FACTOR * (2 * HALF_WIDTH + 1), SCALE_FACTOR * (2 * HALF_HEIGHT + 1)), resample=Image.BOX)
        img = ImageTk.PhotoImage(img)
        w.create_image(0, 0, image=img, anchor="nw")

    process_click(-100, -100)

    root.mainloop()
