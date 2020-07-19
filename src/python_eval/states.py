import collections

# ==============================================================================================================================
class JoinResult(collections.namedtuple('JoinResult', 'budget')):
    
    @staticmethod
    def parse(d):
        return JoinResult(
            d[2][2][0],  # budget
        )
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

