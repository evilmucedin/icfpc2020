import collections
import random
from multiprocessing import Process
from parser import drawState, from_python

from interaction import send2

_, [p1, p2] = send2([1, 0])


def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


def survivor_strategy(state):
    pid = state[2][1]
    actions = []
    my_ships = []
    enemy_ships = []
    for obj in state[3][2]:
        if obj[0][1] == pid:
            print(obj)
            my_ships.append(obj)
        else:
            enemy_ships.append(obj)
    for my_ship in my_ships:
        my_pos = my_ship[0][2]
        thrust = (sign(my_pos[0]), 0) if abs(my_pos[0]) > abs(my_pos[1]) else (0, sign(my_pos[1]))
        actions.append([0, my_ship[0][0], thrust])
        if enemy_ships:
            enemy_ship = random.choice(enemy_ships)
            enemy_pos = enemy_ship[0][2]
            enemy_speed = enemy_ship[0][3]
            actions.append([2, my_ship[0][0], (enemy_pos[0] + enemy_speed[0], enemy_pos[1] + enemy_speed[1]), 5])
    return actions


# ==============================================================================================================================

class ShipState(collections.namedtuple('ShipState', 'player id x y vx vy fuel laser regen lives heat max_heat hzchto')):

    @staticmethod
    def parse(d):
        return ShipState(
            d[0],  # player
            d[1],  # id
            d[2][0],  # x
            d[2][1],  # y
            d[3][0],  # vx
            d[3][1],  # vy
            d[4][0],  # fuel
            d[4][1],  # laser
            d[4][2],  # regen
            d[4][3],  # lives
            d[5],  # heat
            d[6],  # max_heat
            d[7])  # hzchto todo

    def total_hp(self):
        return self.fuel + self.laser + self.regen + self.lives

    def explode(self):
        return [1, self.id]

    def engine(self, dx, dy):
        assert abs(dx) <= self.lives
        assert abs(dy) <= self.lives
        return [0, self.id, (dx, dy)]


ship_state = ShipState.parse([1, 0, (-20, -10), (7, 0), [0, 3, 0, 1], 0, 64, 1])
assert ship_state.x == -20
assert ship_state.vx == 7
assert ship_state.laser == 3


# ==============================================================================================================================


class ShipAction(collections.namedtuple('ShipAction', [])):
    @staticmethod
    def parse(d):
        return ShipAction()


# ==============================================================================================================================

class Ship(collections.namedtuple('Ship', 'state last_actions')):

    @staticmethod
    def parse(d):
        return Ship(ShipState.parse(d[0]),  # state
                    [ShipAction.parse(x) for x in d[1]])  # last_actions


# ==============================================================================================================================


class State(collections.namedtuple('State', 'step me planet_size field_size ships')):

    @staticmethod
    def parse(d):
        game = d[3]
        return State(game[0],  # step
                     d[2][1],  # me
                     game[1][0],  # planet_size
                     game[1][1],  # field_size
                     [Ship.parse(x) for x in game[2]])  # ships

    def player_ships(self, player):
        return [x for x in self.ships if x.state.player == player]


# ==============================================================================================================================


def id_strategy(state):
    print('= ID STRATEGY =')
    parsed_state = State(state)
    print('===============')

    return []


def die_strategy(state):
    print('=====HANG======')
    st = State.parse(state)
    ship = st.player_ships(st.me)[0].state
    print('===============')
    return [ship.explode()]


def move_towards(x, vx, tx):
    """
    x - where we are; vx - our speed; tx - where we want to be.
    Returns optimal engine power.
    Speeds up only if we can later stop without overshoooting.
    Slows down if not slowing down would result in overshooting.
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
        ship = st.player_ships(st.me)[0].state
        mid = (st.field_size + st.planet_size) / 2
        x, y = -ship.y, ship.x
        n = max(abs(x), abs(y))
        x, y = mid * x / n, mid * y / n
        dx = move_towards(ship.x, ship.vx, x)
        dy = move_towards(ship.y, ship.vy, y)
        print('===============')
        if (dx or dy) and ship.fuel:
            return [ship.engine(dx, dy)]
        else:
            return []


def player(id, key, strategy):
    fake_state = from_python(
        [6, [0, 10, -1, id, 0, 2, [], [], 4, [], [256, 1, [448, 1, 64], [16, 128], []], [], []], 9, []])
    send2([2, key, []])
    state = send2([3, key, [128, 5, 13, 1]])
    images = []
    while True:
        state = send2([4, key, strategy(state)])
        images.append(drawState(fake_state, from_python(state))[1])
        if state[1] == 2:
            print('done')
            break
    images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])


strategy1 = RotatingStrategy()
strategy2 = RotatingStrategy()
p1 = Process(target=player, args=p1 + [strategy1.apply])
p2 = Process(target=player, args=p2 + [strategy2.apply])
p1.start()
p2.start()
p1.join()
p2.join()
