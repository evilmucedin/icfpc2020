import random

from constants import *
from orbit_util import trace_orbit, sign
from states import ATACKER
from states import State, JoinResult, ThrustPredictor, Thrust


def min_abs_diff(x, y):
    return min(abs(x), abs(y))



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

class OrbiterStrategy(object):
    def __init__(self, do_laser, printships, duplicate):
        self.do_laser = do_laser
        self.printships = printships
        self.duplicate = duplicate
        self.T = 0
        self.birthday = {}
        self.thrust_predictors = {}

    def pick_stats(self, res):
        joinres = JoinResult.parse(res)
        if joinres.budget > 490:  # atacker
            laser = 64
            regen = 10
            lives = 2
        else:
            laser = 16
            regen = 16
            lives = 8
        fuel = joinres.budget - LASER_COST * laser - REGEN_COST * regen - LIVES_COST * lives
        return [fuel, laser, regen, lives]

    def choose_target(self, my_ship, thrust_action, enemy_ships):
        maxp = 0
        ship = None
        for enemy_ship in enemy_ships:
            predicted_thrust = self.thrust_predictors[enemy_ship.id].predict()
            enemy_pos = enemy_ship.next_round_expected_location(predicted_thrust)
            laser_power = my_ship.laser_power(thrust_action, enemy_pos[0], enemy_pos[1])
            if laser_power > maxp:
                maxp = laser_power
                ship = enemy_ship
        return ship

    def asses_laser_power(self, my_ship, will_move, ex, ey):
        can_take_heat = my_ship.max_heat + my_ship.regen - my_ship.heat - (THRUST_HEAT if will_move else 0)
        x, y = my_ship.next_round_expected_location()
        dist = abs(x - ex) + abs(y - ey)
        pw = min(can_take_heat, my_ship.laser)
        if pw * 3 - dist > 40 or pw == my_ship.laser:
            return pw
        return 0

    def apply(self, state):
        self.T += 1
        st = State.parse(state)
        actions = []

        for ship in st.ships:
            if ship.id not in self.thrust_predictors:
                self.thrust_predictors[ship.id] = ThrustPredictor()
            self.thrust_predictors[ship.id].add(ship.last_actions)

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
            print(f'T:{self.T} Player {st.me}:' + '\n' + "\n".join(str(s) for s in my_ships))
        for my_ship in my_ships:
            my_ship = my_ship
            birthday = self.birthday[my_ship.id]
            age = self.T - birthday
            if self.duplicate and my_ship.lives > 1 and self.T > 5:
                actions.append(my_ship.do_duplicate())
            my_pos = [my_ship.x, my_ship.y]
            my_vel = [my_ship.vx, my_ship.vy]
            cur_closest, cur_farthest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1])
            thrust = (0, 0)
            if cur_closest <= 17:
                thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (
                    sign(my_pos[1]), -sign(my_pos[1]))
            if cur_farthest > st.field_size:
                thrust = (sign(my_vel[0]), sign(my_vel[1]))

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
                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)
                x = thrust[0] if thrust[0] == dx else thrust[0] + dx
                y = thrust[1] if thrust[1] == dy else thrust[0] + dy
                thrust = x, y

            if len(enemy_ships) == 1 and random.random() < self.T / 255.0 and st.me == ATACKER:
                enemy_ship = enemy_ships[0]
                predicted_thrust = self.thrust_predictors[enemy_ship.id].predict()
                ex, ey = enemy_ship.next_round_expected_location(predicted_thrust)
                x = move_towards(my_ship.x, my_ship.vx, ex)
                y = move_towards(my_ship.y, my_ship.vy, ey)
                thrust = x, y

            if my_ship.heat + THRUST_HEAT > my_ship.max_heat:
                thrust = 0, 0

            will_move = (thrust != (0, 0))

            actions.append([0, my_ship.id, thrust])
            thrust_action = Thrust(*thrust)
            enemy_ship = self.choose_target(my_ship, thrust_action, enemy_ships)
            if enemy_ship:
                predicted_thrust = self.thrust_predictors[enemy_ship.id].predict()
                ex, ey = enemy_ship.next_round_expected_location(predicted_thrust)
                next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
                approach_speed = my_ship.approach_speed(enemy_ship, next_dist)
                if my_ship.laser and self.do_laser:
                    power = self.asses_laser_power(my_ship, will_move, ex, ey)
                    if power > 0 and approach_speed < 1:
                        actions.append(my_ship.do_laser(ex, ey, power))
                if next_dist < 5 and st.me == ATACKER and self.T > 7 and len(my_ships) >= len(enemy_ships):
                    actions.append(my_ship.do_explode())
        return actions
