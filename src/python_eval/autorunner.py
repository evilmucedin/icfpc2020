import random
from multiprocessing import Process
from parser import drawState, from_python

from interaction import send2
from orbit_util import sign, trace_orbit
from states import State

_, [p1, p2] = send2([1, 0])

def survivor_strategy(state):
    pid = state[2][1]
    actions = []
    my_ships = []
    enemy_ships = []
    for obj in state[3][2]:
        if obj[0][0] == pid:
            print(obj)
            my_ships.append(obj)
        else:
            enemy_ships.append(obj)
    for my_ship in my_ships:
        my_pos = my_ship[0][2]
        thrust = (-sign(my_pos[0]), 0) if abs(my_pos[0]) > abs(my_pos[1]) else (0, -sign(my_pos[1]))
        actions.append([0, my_ship[0][1], thrust])
        if enemy_ships:
            enemy_ship = random.choice(enemy_ships)
            enemy_pos = enemy_ship[0][2]
            enemy_speed = enemy_ship[0][3]
            actions.append([2, my_ship[0][1], (enemy_pos[0] + enemy_speed[0], enemy_pos[1] + enemy_speed[1]), 5])
    return actions


def id_strategy(state):
    print('= ID STRATEGY =')
    State.parse(state)
    print('===============')

    return []


def die_strategy(state):
    print('=====HANG======')
    st = State.parse(state)
    ship = st.player_ships(st.me)[0]
    print('===============')
    return [ship.do_explode()]


def move_towards(x, vx, tx):
    """
    x - where we are; vx - our speed; tx - where we want to be.
    Returns optimal do_thrust power.
    Speeds up only if we can later stop without overshoooting.
    Slows down if not slowing down would result in overdo_lasering.
    """
    if x == tx:
        return sign(vx)
    s = sign(tx - x)
    if s == -1:
        x, vx, tx = -x, -vx, -tx

    def can_stop(x, vx):
        return x + vx * (vx - 1) // 2 <= tx

    if can_stop(x + vx + 1, vx + 1):
        return -s
    elif can_stop(x + vx, vx):
        return 0
    else:
        return s


assert move_towards(1, 0, 2) == -1
assert move_towards(1, 1, 2) == 0
assert move_towards(1, 3, 2) == 1
assert move_towards(1, 3, 7) == 0
assert move_towards(1, 3, 6) == 1
assert move_towards(1, 3, 20) == -1


class RotatingStrategy(object):
    def __init__(self):
        self.field1 = []
        self.field2 = {}

    def apply(self, state):
        self.field1.append('blablabla')
        self.field2['abc'] = 'def'

        print('=====ROTATE====')
        st = State.parse(state)
        print(st)
        ship = st.player_ships(st.me)[0]
        mid = (st.field_size + st.planet_size) / 2
        x, y = -ship.y, ship.x
        n = max(abs(x), abs(y))
        x, y = mid * x / n, mid * y / n
        dx = move_towards(ship.x, ship.vx, x)
        dy = move_towards(ship.y, ship.vy, y)
        print('===============')
        if (dx or dy) and ship.fuel:
            return [ship.do_thrust(dx, dy)]
        else:
            return []


class OrbiterStrategy(object):
    def __init__(self, do_laser, printships, duplicate):
        self.do_laser = do_laser
        self.printships = printships
        self.duplicate = duplicate
        self.T = 0
        self.birthday = {}

    def apply(self, state):
        self.T += 1
        st = State.parse(state)
        actions = []
        my_ships = []
        enemy_ships = []
        for some_ship in st.ships:
            if some_ship.id not in self.birthday:
                self.birthday[some_ship.id] = self.T
            if some_ship.player == st.me:
                my_ships.append(some_ship)
            else:
                enemy_ships.append(some_ship)
        if self.printships:
            print(f'T:{self.T} Player {st.me}: {" ".join(str([s.fuel, s.laser, s.regen, s.lives]) for s in my_ships)}')
        for my_ship in my_ships:
            my_ship = my_ship
            birthday = self.birthday[my_ship.id]
            age = self.T - birthday
            if self.duplicate and my_ship.lives > 1 and self.T > 10:
                actions.append(my_ship.do_duplicate())
            my_pos = [my_ship.x, my_ship.y]
            my_vel = [my_ship.vx, my_ship.vy]
            cur_closest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1])
            thrust = (0, 0)
            if cur_closest <= 17:
                thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (
                sign(my_pos[1]), -sign(my_pos[1]))

            # find closest friend - if too close randomize movement (include velocity in distance computation)
            closest_ship, dist = None, 1000
            for other in my_ships:
                if other.id == my_ship.id:
                    continue
                od = abs(other.x - my_ship.x) + abs(other.y - my_ship.y) + abs(other.vx - my_ship.vx) + abs(
                    other.vy - my_ship.vy)
                if od < dist:
                    dist = od
                    closest_ship = other
            if closest_ship and dist < 4:
                thrust = (random.randint(-1, 1), random.randint(-1, 1))

            actions.append([0, my_ship.id, thrust])
            if enemy_ships:
                enemy_ship = random.choice(enemy_ships)
                if my_ship.laser and self.do_laser:
                    ex, ey = enemy_ship.next_round_expected_location()
                    actions.append(my_ship.do_laser(ex, ey))
        return actions


def player(id, key, strategy):
    res = send2([2, key, []])
    total = res[2][2][0]
    fake_state = from_python(
        [6, [0, 10, -1, id, 0, 2, [], [], 4, [], [256, 1, [total, 1, 64], [16, 128], []], [], []], 9, []])
    print(f'Send 2 res: {res}, available: {total}')
    las = 8
    regen = 8
    lives = 8
    fuel = total - 4 * las - 12 * regen - 2 * lives
    state = send2([3, key, [fuel, las, regen, lives]])
    images = []
    T = 0
    while True:
        T += 1
        state = send2([4, key, strategy(state)])
        images.append(drawState(fake_state, from_python(state))[1])
        # intermediate gif saves
        if T % 10 == 0:
            images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])
        if state[1] == 2:
            print('done')
            break
    images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])


strategy1 = OrbiterStrategy(do_laser=True, printships=True, duplicate=False)
strategy2 = OrbiterStrategy(do_laser=False, printships=True, duplicate=True)
p1 = Process(target=player, args=p1 + [strategy1.apply])
p2 = Process(target=player, args=p2 + [strategy2.apply])
p1.start()
p2.start()
p1.join()
p2.join()
