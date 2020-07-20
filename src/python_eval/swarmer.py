import random

from constants import *
from orbit_util import sign, get_dist_to_good, gravity_step
from states import State, JoinResult, ThrustPredictor, Thrust, dist as distfun


def min_abs_diff(x, y):
    return min(abs(x), abs(y))

def stat_cost(x):
    return x[0] + LASER_COST * x[1] + REGEN_COST * x[2] + LIVES_COST * x[3]

class SwarmerStrategy(object):
    def __init__(self, printships=False):
        self.T = 0
        self.laser_ship_stats = [20, 32, 8, 1]
        self.thrust_predictors = {}
        self.mothership_id = None
        self.printships = printships

    def pick_stats(self, res):
        joinres = JoinResult.parse(res)
        laser_budget = stat_cost(self.laser_ship_stats)
        swarm_budget = joinres.budget - laser_budget
        n = swarm_budget // 4
        swarm_fuel = swarm_budget - LIVES_COST * n
        return [swarm_fuel + self.laser_ship_stats[0], self.laser_ship_stats[1], self.laser_ship_stats[2], n + 1]

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
        predicted_thrust = self.thrust_predictors[
            enemy_ship.id].predict_only_call_from_precompute() if enemy_ship.fuel > 0 else Thrust(0, 0)
        ex, ey = enemy_ship.next_round_expected_location(predicted_thrust)
        self.enemy_location[enemy_ship.id] = ex, ey
        self.enemy_thrust[enemy_ship.id] = predicted_thrust

    # for mothership only
    def choose_explode_target(self, my_ship, thrust_action, enemy_ships):
        mindist = 10000
        ship = None
        if len(enemy_ships) == 0:
            return enemy_ships[0]
        for enemy_ship in enemy_ships:
            predicted_thrust = self.enemy_thrust[enemy_ship.id]
            dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
            if dist < mindist:
                mindist = dist
                ship = enemy_ship
        return ship

    def choose_laser_target(self, my_ship, thrust_action, enemy_ships):
        maxp = 0
        ship = None
        for enemy_ship in enemy_ships:
            predicted_thrust = self.enemy_thrust[enemy_ship.id]
            enemy_pos = self.enemy_location[enemy_ship.id]
            laser_power = my_ship.laser_power(thrust_action, enemy_pos[0], enemy_pos[1])
            if laser_power > 0 and laser_power + enemy_ship.fuel > maxp:
                maxp = laser_power + enemy_ship.fuel
                ship = enemy_ship
        return ship

    def asses_laser_power(self, my_ship, thrust_action, enemy_ship):
        can_take_heat = my_ship.max_heat + my_ship.regen - my_ship.heat - (
            THRUST_HEAT if thrust_action != Thrust(0, 0) else 0)
        pw = min(can_take_heat, my_ship.laser)

        predicted_thrust = self.enemy_thrust[enemy_ship.id]
        enemy_pos = self.enemy_location[enemy_ship.id]

        laser_power = my_ship.laser_power(thrust_action, enemy_pos[0], enemy_pos[1], pw)

        if laser_power > 0:
            return pw
        return 0

    def get_mothership_actions(self, my_ship, st, enemy_ships):
        # we need to spawn swarm first thing
        actions = []
        if my_ship.lives > 1:
            swarm_fuel = max(my_ship.fuel - self.laser_ship_stats[0], 0)
            for n in range(my_ship.lives-1, 0, -1):
                f = (swarm_fuel * n) // (my_ship.lives - 1)
                if 2 * (f + n) >= my_ship.total_hp():
                    continue
                actions.append(my_ship.do_duplicate_from_mothership(f, n))
                break

        my_pos = [my_ship.x, my_ship.y]
        my_vel = [my_ship.vx, my_ship.vy]
        cur_closest, cur_farthest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1], 265 - self.T)
        thrust = (0, 0)
        if cur_closest <= 24:
            thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (
                sign(my_pos[1]), -sign(my_pos[1]))
        if cur_farthest > st.field_size:
            thrust = (sign(my_vel[0]), sign(my_vel[1]))

        if my_ship.heat + THRUST_HEAT > my_ship.max_heat:
            thrust = 0, 0

        actions.append([0, my_ship.id, thrust])
        thrust_action = Thrust(*thrust)
        enemy_ship = self.choose_laser_target(my_ship, thrust_action, enemy_ships)
        if enemy_ship:
            predicted_thrust = self.enemy_thrust[enemy_ship.id]
            ex, ey = self.enemy_location[enemy_ship.id]
            next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
            if my_ship.laser:
                power = self.asses_laser_power(my_ship, thrust_action, enemy_ship)
                if power > 0:
                    actions.append(my_ship.do_laser(ex, ey, power))

        enemy_ship = self.choose_explode_target(my_ship, thrust_action, enemy_ships)
        if my_ship.lives == 1 and enemy_ship:
            predicted_thrust = self.enemy_thrust[enemy_ship.id]
            next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
            if next_dist < 6 and st.me == ATACKER and self.T > 7 and len(my_ships) >= len(enemy_ships):
                actions = [my_ship.do_explode()]
            if next_dist < 6 and st.me == DEFENDER and self.T > 7 and len(my_ships) > len(enemy_ships):
                actions = [my_ship.do_explode()]
        return actions


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
                if self.mothership_id == None:
                    self.mothership_id = some_ship.id
                my_ships.append(some_ship)
            else:
                enemy_ships.append(some_ship)
                self.precompute_enemy_stuff(some_ship)
        orbits = {}
        if self.printships:
            print(f'T:{self.T} Player {st.me}:' + '\n' + "\n".join(str(s) for s in my_ships))
        for my_ship in my_ships:
            if my_ship.id == self.mothership_id:
                actions.extend(self.get_mothership_actions(my_ship, st, enemy_ships))
                continue
            orbit = (my_ship.x, my_ship.y, my_ship.vx, my_ship.vy)
            if orbit not in orbits:
                orbits[orbit] = []
            orbits[orbit].append(my_ship)

        for orbit, orbit_ships in orbits.items():
            orbit_dist_to_good = get_dist_to_good(*orbit)
            # print('dist', orbit_dist_to_good, len(orbit_ships))
            if len(orbit_ships) > 1:
                possible_thrusts = []
                target_dist = 3 if sum(ship.lives for ship in orbit_ships) >= 32 else 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx == 0 and dy == 0:
                            continue
                        new_dist_to_good = get_dist_to_good(
                            *gravity_step(orbit[0], orbit[1], orbit[2] + dx, orbit[3] + dy))
                        if new_dist_to_good is not None and new_dist_to_good < target_dist:
                            target_dist = new_dist_to_good
                            possible_thrusts = []
                        if new_dist_to_good is not None and new_dist_to_good == target_dist:
                            possible_thrusts.append((-dx, -dy))
                if possible_thrusts:
                    random.shuffle(possible_thrusts)
                    for ship, thrust in zip(orbit_ships[1:], possible_thrusts):
                        actions.append([0, ship.id, thrust])
                continue
            my_ship = orbit_ships[0]
            if orbit_dist_to_good is not None and orbit_dist_to_good > 0:
                possible_thrusts = []
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_dist_to_good = get_dist_to_good(
                            *gravity_step(orbit[0], orbit[1], orbit[2] + dx, orbit[3] + dy))
                        if new_dist_to_good is not None and new_dist_to_good == orbit_dist_to_good - 1:
                            possible_thrusts.append((-dx, -dy))
                assert possible_thrusts
                thrust = random.choice(possible_thrusts)
                actions.append([0, my_ship.id, thrust])
                continue
            if orbit_dist_to_good == 0 and my_ship.lives > 1:
                actions.append(my_ship.do_duplicate_even())
                continue

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
            if closest_ship and dist < 2 and my_ship.vx == closest_ship.vx and my_ship.vy == closest_ship.vy and my_ship.heat + THRUST_HEAT <= my_ship.max_heat and my_ship.fuel > 0:
                possible_thrusts = []
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_dist_to_good = get_dist_to_good(
                            *gravity_step(orbit[0], orbit[1], orbit[2] + dx, orbit[3] + dy))
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
                vx, vy = my_ship.next_vec_to_other(enemy_ship, predicted_thrust)
                if my_ship.fuel >= 2 and distfun(vx, vy) >= 2 and my_ship.can_take_heat() >= 2 * THRUST_HEAT and my_ship.max_dv == 2:
                    vx = -2 * sign(vx) if abs(vx) > 1 else -sign(vx)
                    vy = -2 * sign(vy) if abs(vy) > 1 else -sign(vy)
                    thrust_action = Thrust(vx, vy)
                elif my_ship.fuel >= 1 and distfun(vx, vy) >= 1 and my_ship.can_take_heat() >= THRUST_HEAT:
                    thrust_action = Thrust(-sign(vx), -sign(vy))
                if thrust_action != Thrust(0, 0):
                    actions.append(my_ship.do_thrust(*thrust_action))
                next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
                if my_ship.explode_power(next_dist) and self.T > 7 and len(my_ships) >= len(enemy_ships):
                    print('boom!')
                    actions.append(my_ship.do_explode())
        return actions
