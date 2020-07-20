from orbit_util import trace_orbit, sign
import random
from states import State, JoinResult
from constants import *
from states import State, JoinResult, ThrustPredictor, Thrust

'''
def orbiter_strategy(state):
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
        my_vel = my_ship[0][3]
        cur_closest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1])
        thrust = (0, 0)
        if cur_closest <= 17:
            thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (sign(my_pos[1]), -sign(my_pos[1]))
        actions.append([0, my_ship[0][1], thrust])
        if enemy_ships:
            enemy_ship = random.choice(enemy_ships)
            enemy_pos = enemy_ship[0][2]
            enemy_speed = enemy_ship[0][3]
            actions.append([2, my_ship[0][1], (enemy_pos[0] + enemy_speed[0], enemy_pos[1] + enemy_speed[1]), 5])
    return actions
'''

class OrbiterStrategyOld(object):
    def __init__(self, do_laser, printships, duplicate):
        self.do_laser = do_laser
        self.printships = printships
        self.duplicate = duplicate
        self.T = 0
        self.birthday = {}

    def pick_stats(self, res):
        joinres = JoinResult.parse(res)
        laser = 5
        regen = 13
        lives = 1
        fuel = joinres.budget - 4 * laser - 12 * regen - 2 * lives
        return [fuel, laser, regen, lives]

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

class TestStrategy(object):
    def __init__(self):
        self.k = 1

    def pick_stats(self, res):
        joinres = JoinResult.parse(res)
        laser = 64
        regen = 13
        lives = 1
        fuel = joinres.budget - LASER_COST * laser - REGEN_COST * regen - LIVES_COST * lives
        return [fuel, laser, regen, lives]

    def apply(self, state):
        st = State.parse(state)

        pid = state[2][1]
        actions = []
        my_ships = []
        enemy_ships = []

        my_ships = []
        enemy_ships = []
        for some_ship in st.ships:
            if some_ship.player == st.me:
                my_ships.append(some_ship)
            else:
                enemy_ships.append(some_ship)

        print(f'Player test:' + '\n' + "\n".join(str(s) for s in my_ships))
        for my_ship in my_ships:
            my_pos = [my_ship.x, my_ship.y]
            my_vel = [my_ship.vx, my_ship.vy]
            cur_closest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1])
            thrust = (0, 0)
            thrust = (-sign(my_pos[0]), 0) if abs(my_pos[0]) > abs(my_pos[1]) else (0, -sign(my_pos[1]))
            actions.append([0, my_ship.id, thrust])
            if my_ship.heat == 0:
                self.k += 1
                actions.append(my_ship.do_laser(-my_ship.x + self.k - 4, -my_ship.y, 64))
        return actions
