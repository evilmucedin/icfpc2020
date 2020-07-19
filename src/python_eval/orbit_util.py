import numpy as np

def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0

def trace_orbit(x, y, vx, vy, steps=256):
    closest = max(abs(x), abs(y))
    for it in range(steps):
        if abs(x) >= abs(y):
            vx -= sign(x)
        if abs(y) >= abs(x):
            vy -= sign(y)
        x += vx
        y += vy
        closest = min(closest, max(abs(x), abs(y)))
    return closest

print(trace_orbit(-3, -48, -1, 1))
print(trace_orbit(-3, -48, -1, 1))