import collections
from multiprocessing import Process
from parser import drawState, from_python

from interaction import send2

_, [p1, p2] = send2([1, 0])

# ==============================================================================================================================

ShipStateBase = collections.namedtuple('ShipState', 'player id x y vx vy fuel laser regen lives heat max_heat hzchto')


class ShipState(ShipStateBase):

    def __new__(cls, d):
        return ShipStateBase.__new__(cls,
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
        return [1, 0]

    def engine(self, dx, dy):
        assert abs(dx) <= self.lives
        assert abs(dy) <= self.lives
        return [self.player, (dx, dy)]


ship_state = ShipState([1, 0, (-20, -10), (7, 0), [0, 3, 0, 1], 0, 64, 1])
assert ship_state.x == -20
assert ship_state.vx == 7
assert ship_state.laser == 3

# ==============================================================================================================================

ShipActionBase = collections.namedtuple('ShipAction', [])


class ShipAction(ShipActionBase):
    def __new__(cls, d):
        return ShipActionBase.__new__(cls)


# ==============================================================================================================================

ShipBase = collections.namedtuple('Ship', 'state last_actions')


class Ship(ShipBase):
    def __new__(cls, d):
        return ShipBase.__new__(cls,
                                ShipState(d[0]),  # state
                                [ShipAction(x) for x in d[1]])  # last_actions


# ==============================================================================================================================


StateBase = collections.namedtuple('State', 'step planet_size field_size ships')


class State(StateBase):

    def __new__(cls, d):
        game = d[3]
        return StateBase.__new__(cls,
                                 game[0],  # step
                                 game[1][0],  # planet_size
                                 game[1][1],  # field_size
                                 [Ship(x) for x in game[2]])  # ships

    def player_ships(self, player):
        return [x for x in self.ships if x.state.player == player]


# ==============================================================================================================================


def id_strategy(my_id, state):
    print('= ID STRATEGY =')
    parsed_state = State(state)
    print(my_id, parsed_state)
    print('===============')

    return []

def die_strategy(my_id, state):
    print('=====HANG======')
    st = State(state)
    ship = st.player_ships(my_id)[0].state
    print('===============')
    return [ship.explode()]


def hang_middle_strategy(my_id, state):
    print('=====HANG======')
    st = State(state)
    ship = st.player_ships(my_id)[0].state
    mid = (st.field_size + st.planet_size) / 2
    if abs(ship.x) > mid == ship.x > 0:
        dx = -1
    else:
        dx = 1
    if abs(ship.y) > mid == ship.y > 0:
        dy = -1
    else:
        dy = 1
    print('===============')
    return [ship.engine(dx, dy)]


def player(id, key, strategy):
    fake_state = from_python(
        [6, [0, 10, -1, id, 0, 2, [], [], 4, [], [256, 1, [448, 1, 64], [16, 128], []], [], []], 9, []])
    send2([2, key, []])
    state = send2([3, key, [0, 0, 0, 1]])
    print(state)
    images = []
    while True:
        state = send2([4, key, strategy(id, state)])
        images.append(drawState(fake_state, from_python(state))[1])
        if state[1] == 2:
            print('done')
            break
    images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])


p1 = Process(target=player, args=p1 + [id_strategy])
p2 = Process(target=player, args=p2 + [hang_middle_strategy])
p1.start()
p2.start()
p1.join()
p2.join()
