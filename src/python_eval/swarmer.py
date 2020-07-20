import random

from constants import *
from orbit_util import trace_orbit, sign, get_dist_to_good, gravity_step
from states import ATACKER
from states import State, JoinResult, ThrustPredictor, Thrust

def min_abs_diff(x, y):
    return min(abs(x), abs(y))

class SwarmerStrategy(object):
    def __init__(self):
        self.T = 0
        self.thrust_predictors = {}

    def pick_stats(self, res):
        joinres = JoinResult.parse(res)
        if joinres.budget > 490: # attacker
            laser = 64
            regen = 10
            lives = 2
        else:
            laser = 16
            regen = 16
            lives = 8
        n = joinres.budget // 4
        return [joinres.budget - 2 * n, 0, 0, n]

    def choose_target(self, my_ship, thrust_action, enemy_ships):
        dist = 10000
        ship = None
        my_pos = my_ship.next_round_expected_location(thrust_action)
        for enemy_ship in enemy_ships:
            predicted_thrust = self.enemy_thrust[enemy_ship.id]
            enemy_pos = self.enemy_location[enemy_ship.id]
            coord_diff = min_abs_diff(my_pos[0] - enemy_pos[0], my_pos[1] - enemy_pos[1])
            if coord_diff < dist:
                ship = enemy_ship
                dist = coord_diff
        return ship


    def reset_precomputed(self):
        self.enemy_location = {}
        self.enemy_thrust = {}

    def precompute_enemy_stuff(self, enemy_ship):
        predicted_thrust = self.thrust_predictors[enemy_ship.id].predict_only_call_from_precompute() if enemy_ship.fuel > 0 else Thrust(0, 0)
        ex, ey = enemy_ship.next_round_expected_location(predicted_thrust)
        self.enemy_location[enemy_ship.id] = ex, ey
        self.enemy_thrust[enemy_ship.id] = predicted_thrust

    def apply(self, state):
        self.T += 1
        # assert self.T < 32
        st = State.parse(state)
        self.reset_precomputed()
        actions = []

        for ship in st.ships:
            if ship.id not in self.thrust_predictors:
                self.thrust_predictors[ship.id] = ThrustPredictor()
            self.thrust_predictors[ship.id].add(ship.last_actions)

        my_ships = []
        enemy_ships = []
        for some_ship in st.ships:
            if some_ship.player == st.me:
                my_ships.append(some_ship)
            else:
                enemy_ships.append(some_ship)
                self.precompute_enemy_stuff(some_ship)
        orbits = {}
        for my_ship in my_ships:
            orbit = (my_ship.x, my_ship.y, my_ship.vx, my_ship.vy)
            if orbit not in orbits:
                orbits[orbit] = []
            orbits[orbit].append(my_ship)
        
        for orbit, orbit_ships in orbits.items():
            orbit_dist_to_good = get_dist_to_good(*orbit)
            # print('dist', orbit_dist_to_good, len(orbit_ships))
            if len(orbit_ships) > 1:
                possible_thrusts = []
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_dist_to_good = get_dist_to_good(*gravity_step(orbit[0], orbit[1], orbit[2] + dx, orbit[3] + dy))
                        if new_dist_to_good is not None and new_dist_to_good == 0:
                            possible_thrusts.append((-dx, -dy))
                if possible_thrusts:
                    for ship in orbit_ships:
                        thrust = random.choice(possible_thrusts)
                        actions.append([0, ship.id, thrust])
                continue
            my_ship = orbit_ships[0]
            if orbit_dist_to_good is not None and orbit_dist_to_good > 0:
                possible_thrusts = []
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_dist_to_good = get_dist_to_good(*gravity_step(orbit[0], orbit[1], orbit[2] + dx, orbit[3] + dy))
                        if new_dist_to_good is not None and new_dist_to_good == orbit_dist_to_good - 1:
                            possible_thrusts.append((-dx, -dy))
                assert possible_thrusts
                thrust = random.choice(possible_thrusts)
                actions.append([0, my_ship.id, thrust])
                continue
            if orbit_dist_to_good == 0 and my_ship.lives > 1:
                actions.append(my_ship.do_duplicate())
                continue
            # birthday = self.birthday[my_ship.id]
            # age = self.T - birthday
            # if self.duplicate and my_ship.lives > 1 and self.T > 5:
            #     actions.append(my_ship.do_duplicate())
            # my_pos = [my_ship.x, my_ship.y]
            # my_vel = [my_ship.vx, my_ship.vy]
            # cur_closest, cur_farthest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1])
            # thrust = (0, 0)
            # if cur_closest <= 17:
            #     thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (
            #         sign(my_pos[1]), -sign(my_pos[1]))
            # if cur_farthest > st.field_size:
            #     thrust = (sign(my_vel[0]), sign(my_vel[1]))

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
            if closest_ship and dist < 4 and my_ship.heat + THRUST_HEAT <= my_ship.max_heat and my_ship.fuel > 0:
                possible_thrusts = []
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_dist_to_good = get_dist_to_good(*gravity_step(orbit[0], orbit[1], orbit[2] + dx, orbit[3] + dy))
                        if new_dist_to_good is not None and new_dist_to_good == 0:
                            possible_thrusts.append((-dx, -dy))
                if possible_thrusts:
                    thrust = random.choice(possible_thrusts)
                    actions.append([0, my_ship.id, thrust])
                    continue
            if enemy_ships:
                thrust_action = Thrust(0, 0)
                enemy_ship = self.choose_target(my_ship, thrust_action, enemy_ships)
                predicted_thrust = self.enemy_thrust[enemy_ship.id]
                ex, ey = self.enemy_location[enemy_ship.id]
                next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
                approach_speed = my_ship.approach_speed(enemy_ship, next_dist)
                #  and st.me == ATACKER
                if next_dist < 5 and self.T > 7 and len(my_ships) >= len(enemy_ships):
                    print('boom!')
                    actions.append(my_ship.do_explode())
        return actions
