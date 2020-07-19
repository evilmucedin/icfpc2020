import random

from constants import *
from orbit_util import trace_orbit, sign
from states import ATACKER
from states import State, JoinResult, ThrustPredictor, Thrust


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
        laser = 64
        regen = 10
        lives = 2
        fuel = joinres.budget - LASER_COST * laser - REGEN_COST * regen - LIVES_COST * lives
        return [fuel, laser, regen, lives]

    def choose_target(self, my_ship, thrust_action, enemy_ships):
        dist = 10000
        ship = None
        for enemy_ship in enemy_ships:
            predicted_thrust = self.thrust_predictors[enemy_ship.id].predict()
            next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
            if next_dist < dist:
                ship = enemy_ship
                dist = next_dist
        return ship

    def asses_laser_power(self, my_ship, will_move, ex, ey):
        can_take_heat = my_ship.max_heat + my_ship.regen - my_ship.heat - (THRUST_HEAT if will_move else 0)
        x, y = my_ship.next_round_expected_location()
        dist = abs(x - ex) + abs(y - ey)
        pw = min(can_take_heat, my_ship.laser)
        if dist > 150:
            return 0
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

            will_move = (thrust != (0, 0))

            actions.append([0, my_ship.id, thrust])
            if enemy_ships:
                thrust_action = Thrust(*thrust)
                enemy_ship = self.choose_target(my_ship, thrust_action, enemy_ships)
                predicted_thrust = self.thrust_predictors[enemy_ship.id].predict()
                ex, ey = enemy_ship.next_round_expected_location(predicted_thrust)
                next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
                approach_speed = my_ship.approach_speed(enemy_ship, next_dist)
                if my_ship.laser and self.do_laser:
                    power = self.asses_laser_power(my_ship, will_move, ex, ey)
                    if power > 0 and approach_speed < 1:
                        actions.append(my_ship.do_laser(ex, ey, power))
                if next_dist < 7 and st.me == ATACKER and self.T > 7 and len(my_ships) >= len(enemy_ships):
                    actions.append(my_ship.do_explode())
        return actions
