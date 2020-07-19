import collections
import random
from multiprocessing import Process
from parser import drawState, from_python
from orbit_util import sign, trace_orbit
from orbiter import orbiter_strategy

from interaction import send2

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

    def next_round_expected_speed(self):
        vx = self.vx
        vy = self.vy
        if abs(self.x) >= abs(self.y):
            vx += 1 if x < 0 else -1
        if abs(self.y) >= abs(self.x):
            vy += 1 if y < 0 else - 1
        return vx, vy
    
    def next_round_expected_location(self):
        vx, vy = self.next_round_expected_speed()
        return self.x + vx, self.y + vy


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
    State.parse(state)
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

class OrbiterStrategy(object):
    def __init__(self, shoot, printships, duplicate):
        self.shoot = shoot
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
            if some_ship.state.id not in self.birthday:
                self.birthday[some_ship.state.id] = self.T
            if some_ship.state.player == st.me:
                my_ships.append(some_ship)
            else:
                enemy_ships.append(some_ship)
        if self.printships:
            print(f'T:{self.T} Player {st.me}: {" ".join(str([s.state.fuel, s.state.laser, s.state.regen, s.state.lives]) for s in my_ships)}')
        for my_ship in my_ships:
            birthday = self.birthday[my_ship.state.id]
            age = self.T - birthday
            if self.duplicate and my_ship.state.lives > 1 and self.T > 10:
                actions.append([3, my_ship.state.id, [my_ship.state.fuel // 2, my_ship.state.laser // 2, my_ship.state.regen // 2, my_ship.state.lives // 2]])
            my_pos = [my_ship.state.x, my_ship.state.y]
            my_vel = [my_ship.state.vx, my_ship.state.vy]
            cur_closest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1])
            thrust = (0, 0)
            if cur_closest <= 17:
                thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (sign(my_pos[1]), -sign(my_pos[1]))

            # find closest friend - if too close randomize movement (include velocity in distance computation)
            closest_ship, dist = None, 1000
            for other in my_ships:
                if other.state.id == my_ship.state.id: continue
                od = abs(other.state.x - my_ship.state.x) + abs(other.state.y - my_ship.state.y) + abs(other.state.vx - my_ship.state.vx) + abs(other.state.vy - my_ship.state.vy)
                if od < dist:
                    dist = od
                    closest_ship = other
            if closest_ship and dist < 4:
                thrust = (random.randint(-1, 1), random.randint(-1, 1))

            actions.append([0, my_ship.state.id, thrust])
            if enemy_ships:
                enemy_ship = random.choice(enemy_ships)
                enemy_pos = [enemy_ship.state.x, enemy_ship.state.y]
                enemy_speed = [enemy_ship.state.vx, enemy_ship.state.vy]
                if self.shoot:
                    for my_ship in my_ships:
                        actions.append([2, my_ship.state.id, (enemy_pos[0] + enemy_speed[0], enemy_pos[1] + enemy_speed[1]), my_ship.state.laser])

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


strategy1 = OrbiterStrategy(shoot=True, printships=True, duplicate=False)
strategy2 = OrbiterStrategy(shoot=False, printships=True, duplicate=True)
p1 = Process(target=player, args=p1 + [strategy1.apply])
p2 = Process(target=player, args=p2 + [strategy2.apply])
p1.start()
p2.start()
p1.join()
p2.join()
