import collections


def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


def dist(x, y):
    return max(abs(x), abs(y))


# ==============================================================================================================================
class JoinResult(collections.namedtuple('JoinResult', 'budget')):

    @staticmethod
    def parse(d):
        return JoinResult(
            d[2][2][0],  # budget
        )


# ==============================================================================================================================

class Thrust(collections.namedtuple('Thrust', 'x y')):
    pass


class Laser(collections.namedtuple('Laser', 'x y pwr dmg hzchto')):
    pass


class Explode(collections.namedtuple('Explode', [])):
    pass


class ShipAction(collections.namedtuple('ShipAction', [])):
    @staticmethod
    def parse(d):
        if d[0] == 0:
            return Thrust(d[1][0], d[1][1])
        if d[0] == 1:
            return Explode()
        if d[0] == 2:
            return Laser(d[1][0], d[1][1], d[2], d[3], d[4])


# ==============================================================================================================================

ATACKER = 0
DEFENDER = 1


def laser_power(dx, dy, power):
    maxx = abs(dx)
    maxy = abs(dy)
    max_xy = max(maxx, maxy)
    min_xy = min(maxx, maxy)
    d_xy = min_xy if 2 * min_xy < max_xy else max_xy - min_xy
    return 3 * power * (max_xy - 2 * d_xy) // max_xy + 1 - max_xy


class Ship(
    collections.namedtuple('Ship', 'player id x y vx vy fuel laser regen lives heat max_heat max_dv last_actions')):

    @staticmethod
    def parse(d):
        d1, d2 = d
        return Ship(
            d1[0],  # player
            d1[1],  # id
            d1[2][0],  # x
            d1[2][1],  # y
            d1[3][0],  # vx
            d1[3][1],  # vy
            d1[4][0],  # fuel
            d1[4][1],  # laser
            d1[4][2],  # regen
            d1[4][3],  # lives
            d1[5],  # heat
            d1[6],  # max_heat
            d1[7],  # max_dv todo
            [ShipAction.parse(x) for x in d2])

    def total_hp(self):
        return self.fuel + self.laser + self.regen + self.lives

    def do_explode(self):
        return [1, self.id]

    def do_thrust(self, dx, dy):
        assert abs(dx) <= self.lives
        assert abs(dy) <= self.lives
        return [0, self.id, (dx, dy)]

    def do_laser(self, x, y, power=None):
        return [2, self.id, (x, y), self.laser if power is None else power]

    def do_duplicate(self):
        return [3, self.id, [self.fuel // 4, self.laser // 4, self.regen // 4, self.lives // 2]]

    def next_round_expected_speed(self, thrust):
        vx = self.vx - thrust.x
        vy = self.vy - thrust.y
        if abs(self.x) >= abs(self.y):
            vx += -sign(self.x)
        if abs(self.y) >= abs(self.x):
            vy += -sign(self.y)
        return vx, vy

    def next_round_expected_location(self, thrust=Thrust(0, 0)):
        vx, vy = self.next_round_expected_speed(thrust)
        return self.x + vx, self.y + vy

    def approach_speed(self, other, next_dist):
        curr_dist = dist(self.x - other.x, self.y - other.y)
        return curr_dist - next_dist

    def next_dist(self, thrust, other, other_thrust):
        sx, sy = self.next_round_expected_location(thrust)
        ox, oy = other.next_round_expected_location(other_thrust)
        return dist(sx - ox, sy - oy)

    def laser_power(self, thrust, other_x, other_y, power=None):
        if power == None:
            power = self.laser
        x, y = self.next_round_expected_location(thrust)
        return laser_power(x - other_x, y - other_y, power)


ship = Ship.parse([[1, 0, (-20, -10), (7, 0), [0, 3, 0, 1], 0, 64, 1], []])
assert ship.x == -20
assert ship.vx == 7
assert ship.laser == 3

ship = Ship.parse([[1, 0, (0, 0), (0, 0), [0, 32, 3, 1], 0, 64, 1], []])
assert ship.laser_power(Thrust(0, 0), 6, 6) == 91
assert ship.laser_power(Thrust(0, 0), 6, 5) == 59
assert ship.laser_power(Thrust(0, 0), 6, 2) == 27
assert ship.laser_power(Thrust(0, 0), 6, -2) == 27
assert ship.laser_power(Thrust(0, 0), -6, -2) == 27

s1 = Ship.parse([[1, 0, (-20, -10), (7, 0), [0, 3, 0, 1], 0, 64, 1], []])
s2 = Ship.parse([[1, 0, (-20, -10), (7, 10), [0, 3, 0, 1], 0, 64, 1], []])
nd = s1.next_dist(Thrust(0, 0), s2, Thrust(0, 1))
assert s1.approach_speed(s2, nd) == -9

s1 = Ship.parse([[1, 0, (-20, 10), (7, 0), [0, 3, 0, 1], 0, 64, 1], []])
s2 = Ship.parse([[1, 0, (-20, -10), (7, 10), [0, 3, 0, 1], 0, 64, 1], []])
nd = s1.next_dist(Thrust(0, 0), s2, Thrust(0, 1))
assert s1.approach_speed(s2, nd) == 9


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
        return [x for x in self.ships if x.player == player]


# ==============================================================================================================================

class ThrustPredictor(object):

    def __init__(self, decay=0.95, acorr=8):
        self.hist = []
        self.decay = decay
        self.acorr = acorr
        self.lag_w = [0] * (acorr + 1)

    def add(self, actions):
        thrust = Thrust(0, 0)
        for action in actions:
            if type(action) == Thrust:
                thrust = action
                break
        for i in range(1, self.acorr + 1):
            self.lag_w[i] *= self.decay
            if i <= len(self.hist) and thrust == self.hist[-i]:
                self.lag_w[i] += 1
        self.hist.append(thrust)

    def predict(self):
        bestv = 0
        bestk = Thrust(0, 0)
        for i in range(1, self.acorr + 1):
            if self.lag_w[i] > bestv:
                bestv = self.lag_w[i]
                bestk = self.hist[-i]
        # print(bestk)
        # print(self.hist)
        return bestk


tp = ThrustPredictor()
tp.add([Thrust(0, 1)])
tp.add([Thrust(1, 0)])
tp.add([Thrust(1, 0)])
tp.add([Thrust(0, 1)])
tp.add([Thrust(1, 0)])
tp.add([Thrust(1, 0)])
tp.add([Thrust(0, 1)])
assert tp.predict() == Thrust(1, 0)

tp = ThrustPredictor()
tp.add([Thrust(0, 1)])
tp.add([Thrust(0, 1)])
tp.add([Thrust(1, 0)])
tp.add([Thrust(0, 1)])
tp.add([Thrust(0, 1)])
tp.add([Thrust(1, 0)])
tp.add([Thrust(0, 1)])
assert tp.predict() == Thrust(0, 1)

tp = ThrustPredictor()
tp.add([Thrust(0, 1)])
tp.add([Thrust(0, 1)])
assert tp.predict() == Thrust(0, 1)

tp = ThrustPredictor()
tp.add([Thrust(0, 1)])
tp.add([Thrust(1, 0)])
assert tp.predict() == Thrust(0, 0)
