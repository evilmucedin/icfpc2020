import numpy as np

FIELD_SIZE = 128
MAX_VELOCITY = 10

def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0

def gravity_step(x, y, vx, vy):
    if abs(x) >= abs(y):
        vx -= sign(x)
    if abs(y) >= abs(x):
        vy -= sign(y)
    x += vx
    y += vy
    return x, y, vx, vy

def gravity_step_np(x, y, vx, vy):
    vx = vx - np.sign(x) * (abs(x) >= abs(y))
    vy = vy - np.sign(y) * (abs(y) >= abs(x))
    x = x + vx
    y = y + vy
    return x, y, vx, vy

def trace_orbit_np(x, y, vx, vy, steps):
    xs = []
    ys = []
    vxs = []
    vys = []
    for it in range(steps):
        x, y, vx, vy = gravity_step_np(x, y, vx, vy)
        xs.append(x)
        ys.append(y)
        vxs.append(vx)
        vys.append(vy)
    return np.stack(xs, axis=-1), np.stack(ys, axis=-1), np.stack(vxs, axis=-1), np.stack(vys, axis=-1)

def trace_orbit(x, y, vx, vy, steps=256):
    closest = max(abs(x), abs(y))
    farthest = 0
    for it in range(steps):
        x, y, vx, vy = gravity_step(x, y, vx, vy)
        closest = min(closest, max(abs(x), abs(y)))
        farthest = max(farthest, max(abs(x), abs(y)))
    return closest, farthest

def is_good_orbit(x, y, vx, vy, steps=512):
    farthest = 0
    for it in range(steps):
        x, y, vx, vy = gravity_step(x, y, vx, vy)
        dist = max(abs(x), abs(y))
        farthest = max(farthest, dist)
        if dist <= 16 or dist >= 128:
            return False
    return farthest > 100

if __name__ == "__main__":
    cnt = 0
    total = 0
    good_orbits = []
    dist_to_good = np.full((2 * FIELD_SIZE + 1, 2 * FIELD_SIZE + 1, 2 * MAX_VELOCITY + 1, 2 * MAX_VELOCITY + 1), -1, dtype=np.int8)
    rev_edges = np.full((2 * FIELD_SIZE + 1, 2 * FIELD_SIZE + 1, 2 * MAX_VELOCITY + 1, 2 * MAX_VELOCITY + 1), None)
    for x in range(-FIELD_SIZE, FIELD_SIZE + 1):
        print(x)
        for y in range(-FIELD_SIZE, FIELD_SIZE + 1):
            for vx in range(-MAX_VELOCITY, MAX_VELOCITY + 1):
                for vy in range(-MAX_VELOCITY, MAX_VELOCITY + 1):
                    rev_edges[x + FIELD_SIZE, y + FIELD_SIZE, vx + MAX_VELOCITY, vy + MAX_VELOCITY] = []
                    if is_good_orbit(x, y, vx, vy, steps=512):
                        good_orbits.append((x, y, vx, vy))
                        dist_to_good[x + FIELD_SIZE, y + FIELD_SIZE, vx + MAX_VELOCITY, vy + MAX_VELOCITY] = 0
    print(len(good_orbits))
    for x in range(-FIELD_SIZE, FIELD_SIZE + 1):
        print(x)
        for y in range(-FIELD_SIZE, FIELD_SIZE + 1):
            for vx in range(-MAX_VELOCITY, MAX_VELOCITY + 1):
                for vy in range(-MAX_VELOCITY, MAX_VELOCITY + 1):
                    x1, y1, vx1, vy1 = gravity_step(x, y, vx, vy)
                    if -FIELD_SIZE <= x1 <= FIELD_SIZE and -FIELD_SIZE <= y1 <= FIELD_SIZE and -MAX_VELOCITY <= vx1 <= MAX_VELOCITY and -MAX_VELOCITY <= vy1 <= MAX_VELOCITY:
                        rev_edges[x1 + FIELD_SIZE, y1 + FIELD_SIZE, vx1 + MAX_VELOCITY, vy1 + MAX_VELOCITY].append((x, y, vx, vy))
    
    q = list(good_orbits)
    it = 0
    while it < len(q):
        x, y, vx, vy = q[it]
        it += 1
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if -FIELD_SIZE <= x - dx <= FIELD_SIZE and -FIELD_SIZE <= y - dy <= FIELD_SIZE and -MAX_VELOCITY <= vx - dx <= MAX_VELOCITY and -MAX_VELOCITY <= vy - dy <= MAX_VELOCITY:
                    for x1, y1, vx1, vy1, in rev_edges[x - dx + FIELD_SIZE, y - dy + FIELD_SIZE, vx - dx + MAX_VELOCITY, vy - dy + MAX_VELOCITY]:
                        if (abs(x1) > 16 or abs(y1) > 16) and dist_to_good[x1 + FIELD_SIZE, y1 + FIELD_SIZE, vx1 + MAX_VELOCITY, vy1 + MAX_VELOCITY] == -1:
                            dist_to_good[x1 + FIELD_SIZE, y1 + FIELD_SIZE, vx1 + MAX_VELOCITY, vy1 + MAX_VELOCITY] = dist_to_good   [x + FIELD_SIZE, y + FIELD_SIZE, vx + MAX_VELOCITY, vy + MAX_VELOCITY] + 1
                            q.append((x1, y1, vx1, vy1))
    np.savez_compressed('dist_to_good.npz', dist_to_good)

dist_to_good = np.load('dist_to_good.npz')['arr_0']

def get_dist_to_good(x, y, vx, vy):
    if -FIELD_SIZE <= x <= FIELD_SIZE and -FIELD_SIZE <= y <= FIELD_SIZE and -MAX_VELOCITY <= vx <= MAX_VELOCITY and -MAX_VELOCITY <= vy <= MAX_VELOCITY:
        return dist_to_good[x + FIELD_SIZE, y + FIELD_SIZE, vx + MAX_VELOCITY, vy + MAX_VELOCITY]
    return None

# for x in range(-FIELD_SIZE, FIELD_SIZE + 1):
#     for y in range(-FIELD_SIZE, FIELD_SIZE + 1):
#         val = dist_to_good[x + FIELD_SIZE, y + FIELD_SIZE, MAX_VELOCITY, MAX_VELOCITY]
#         print('x' if val == -1 else val, end='')
#     print()