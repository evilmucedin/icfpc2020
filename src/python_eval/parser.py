import sys
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

true = F('t', 2, lambda x, y: x)
false = F('t', 2, lambda x, y: y)

nil = F('nil', 2, lambda x, y: y)
cons = F('cons', 3, cons_f)
vec = F('vec', 3, cons_f)
car = F('car', 1, lambda lst: lst(true))
cdr = F('cdr', 1, lambda lst: lst(false))

def quot(a, b):
    # print('quot', a, b)
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

int1 = symbols['galaxy'](nil, vec(0, 0))
print(eager(car(int1), deep=True))
print(eager(car(cdr(int1)), deep=True))
print(eager(car(cdr(cdr(int1))), deep=True))

# for line in lines:
#     print(line[0], eager(symbols[line[0]]))

# def terminal(a):
#     if a[0] == ':':
#         a = 'var' + a[1:]
#     elif a[0] == '-':
#         a = f'({a})'
#     elif not a[0].isdigit():
#         symbols.add(a)

#     return a
# return
#         a = a[1:]
#         expr1, a = parseExpr(a)
#         expr2, a = parseExpr(a)
#         return f"({expr1} {expr2})", a
#     else:
#         return terminal(a[0]), a[1:]

# for line in lines:
#     assert line[1] == '='
#     expr, rem = parseExpr(line[2:])
#     print(terminal(line[0]), '=', expr)

# # print(symbols)