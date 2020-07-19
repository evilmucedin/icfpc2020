import collections


def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


# ==============================================================================================================================
class JoinResult(collections.namedtuple('JoinResult', 'budget')):
    
    @staticmethod
    def parse(d):
        return JoinResult(
            d[2][2][0],  # budget
        )
# ==============================================================================================================================

class Ship(
    collections.namedtuple('Ship', 'player id x y vx vy fuel laser regen lives heat max_heat hzchto last_actions')):

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
            d1[7],  # hzchto todo
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
        return [3, self.id, [self.fuel // 2, self.laser // 2, self.regen // 2, self.lives // 2]]

    def next_round_expected_speed(self):
        vx = self.vx
        vy = self.vy
        if abs(self.x) >= abs(self.y):
            vx += -sign(self.x)
        if abs(self.y) >= abs(self.x):
            vy += -sign(self.y)
        return vx, vy

    def next_round_expected_location(self):
        vx, vy = self.next_round_expected_speed()
        return self.x + vx, self.y + vy


ship = Ship.parse([[1, 0, (-20, -10), (7, 0), [0, 3, 0, 1], 0, 64, 1], []])
assert ship.x == -20
assert ship.vx == 7
assert ship.laser == 3


# ==============================================================================================================================


class ShipAction(collections.namedtuple('ShipAction', [])):
    @staticmethod
    def parse(d):
        return ShipAction()


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
