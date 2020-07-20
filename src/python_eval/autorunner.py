import random
from multiprocessing import Process
from parser import drawState, from_python
from states import State, JoinResult
from orbiter import OrbiterStrategy
from swarmer import SwarmerStrategy

from interaction import send2
from orbit_util import sign, trace_orbit

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


def player(id, key, strategy):
    res = send2([2, key, [103652820, 192496425430]])
    joinres = JoinResult.parse(res)
    total = joinres.budget
    fake_state = from_python(
        [6, [0, 10, -1, id, 0, 2, [], [], 4, [], [256, 1, [total, 1, 64], [16, 128], []], [], []], 9, []])
    print(f'Send 2 res: {res}, available: {total}')
    initial_stats = strategy.pick_stats(res)
    state = send2([3, key, initial_stats])
    images = []
    T = 0
    while True:
        T += 1
        state = send2([4, key, strategy.apply(state)])
        # images.append(drawState(fake_state, from_python(state))[1])
        # intermediate gif saves
        # if T % 10 == 0:
        #     images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])
        if state[1] == 2:
            print('done')
            break
    # images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])

# print(send2([122, 203, 410, 164, 444, 484, 202, 77, 251, 56, 456, 435, 28, 329, 257, 265, 501, 18, 190, 423, 384, 434, 266, 69, 34, 437, 203, 152, 160, 425, 245, 428, 99, 107, 192, 372, 346, 344, 169, 478, 393, 502, 201, 497, 313, 32, 281, 510, 436, 22, 237, 80, 325, 405, 184, 358, 57, 276, 359, 189, 284, 277, 198, 244]))

strategy2 = SwarmerStrategy(printships=False)
strategy1 = OrbiterStrategy(do_laser=True, printships=True, duplicate=False)
p1 = Process(target=player, args=p1 + [strategy1])
p2 = Process(target=player, args=p2 + [strategy2])
p1.start()
p2.start()
p1.join()
p2.join()
