import random

from constants import *
from orbit_util import trace_orbit, sign
from states import ATACKER, DEFENDER
from states import State, JoinResult, ThrustPredictor, Thrust, laser_power


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

class LaserShipStrategy(object):
    def __init__(self):
        self.time_left = 256

    def find_better_orbit(self, my_ship, st):
        if my_ship.fuel == 0:
            return []
        pos = my_ship.position()
        fft = pos.safe_free_fall_rounds(st, self.time_left)
        best = [0, Thrust(0, 0)]
        for x in range(-2, 3):
            for y in range(-2, 3):
                t = Thrust(x, y)
                cost = min(max(abs(x), abs(y)), 1)
                if cost > my_ship.fuel:
                    continue
                pos_next = pos.next_round_expected(t)
                fft2 = pos_next.safe_free_fall_rounds(st, self.time_left)
                if fft2 - fft > best[0] * cost:
                    best = [(fft2 - fft) / 2, t]
        return [my_ship.do_thrust(best[1].x, best[1].y)] if best[0] > 0 else []

    def apply_orbit(self, my_ship, st):
        tl = min(self.time_left, 20)
        return [] if my_ship.position().safe_free_fall_rounds(st, tl) >= tl else self.find_better_orbit(my_ship, st)

    def apply(self, st, my_ship, enemy_ships):
        self.time_left -= 1
        actions = self.apply_orbit(my_ship, st)
        min_fuel = 10 + self.time_left // 5
        extra_fuel = my_ship.fuel - min_fuel if my_ship.fuel > min_fuel else 0
        max_lp = min(my_ship.laser, my_ship.max_heat - my_ship.heat + my_ship.regen + extra_fuel)
        if (max_lp == 0):
            return actions

        my_pos = my_ship.position()
        my_pos1 = my_pos.next_round_expected()
        my_pos2 = my_pos.next_round_expected()
            
        candidates = []
        for enemy_ship in enemy_ships:
            enemy_pos = enemy_ship.position()
            enemy_pos1 = enemy_pos.next_round_expected()
            # simple logic first
            ldamage = laser_power(enemy_pos1.x - my_pos1.x, enemy_pos1.y - my_pos1.y, max_lp)
            if ldamage <= max_lp:
                continue
            etd =  enemy_ship.energy_to_destroy()
            candidates = candidates + [[enemy_ship, 1 if ldamage >= etd else 0, min(etd, ldamage)]]
        if not candidates:
            return actions
        
        best_candidate = candidates[0]
        enemy_pos = best_candidate[0].position()
        enemy_pos1 = enemy_pos.next_round_expected()
        actions.append(my_ship.do_laser(enemy_pos1.x, enemy_pos1.x, max_lp))
        return actions

class OrbiterStrategy(object):
    def __init__(self, do_laser, printships, duplicate):
        self.do_laser = do_laser
        self.printships = printships
        self.duplicate = duplicate
        self.T = 0
        self.birthday = {}
        self.thrust_predictors = {}
        self.laser_ship = LaserShipStrategy()

    def pick_stats(self, res):
        joinres = JoinResult.parse(res)
        if joinres.budget > 490:  # atacker
            laser = 64
            regen = 10
            lives = 1
        else:
            laser = 16
            regen = 16
            lives = 32
        fuel = joinres.budget - LASER_COST * laser - REGEN_COST * regen - LIVES_COST * lives
        return [fuel, laser, regen, lives]

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
        st = State.parse(state)
        self.reset_precomputed()
        all_actions_of_all_ships = []

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
                self.precompute_enemy_stuff(some_ship)
        if self.printships:
            print(f'T:{self.T} Player {st.me}:' + '\n' + "\n".join(str(s) for s in my_ships))
        for my_ship in my_ships:
            # TODO: beter logic
            # if my_ship.laser > 0 and my_ship.lives == 1:
            #    all_actions_of_all_ships.extend(self.laser_ship.apply(st, my_ship, enemy_ships))
            #    continue
            actions = []
            my_ship = my_ship
            birthday = self.birthday[my_ship.id]
            age = self.T - birthday
            my_pos = [my_ship.x, my_ship.y]
            my_vel = [my_ship.vx, my_ship.vy]
            razduplyaemsya = True
            cur_closest, cur_farthest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1], 265 - self.T)
            thrust = (0, 0)
            if cur_closest <= 24:
                thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (
                    sign(my_pos[1]), -sign(my_pos[1]))
                razduplyaemsya = False
            if cur_farthest > st.field_size:
                thrust = (sign(my_vel[0]), sign(my_vel[1]))
                razduplyaemsya = False

            if self.duplicate and my_ship.lives > 1 and razduplyaemsya:
                actions.append(my_ship.do_duplicate())

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
            if closest_ship and dist < 2 and my_ship.vx == closest_ship.vx and my_ship.vy == closest_ship.vy:
                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)
                x = thrust[0] if thrust[0] == dx else thrust[0] + dx
                y = thrust[1] if thrust[1] == dy else thrust[0] + dy
                thrust = x, y

            # if len(enemy_ships) == 1 and self.T > 200 and st.me == ATACKER:
            #     enemy_ship = enemy_ships[0]
            #     predicted_thrust = self.thrust_predictors[enemy_ship.id].predict()
            #     ex, ey = enemy_ship.next_round_expected_location(predicted_thrust)
            #     x = move_towards(my_ship.x, my_ship.vx, ex)
            #     y = move_towards(my_ship.y, my_ship.vy, ey)
            #     thrust = x, y

            if my_ship.heat + THRUST_HEAT > my_ship.max_heat:
                thrust = 0, 0

            actions.append([0, my_ship.id, thrust])
            thrust_action = Thrust(*thrust)
            enemy_ship = self.choose_laser_target(my_ship, thrust_action, enemy_ships)
            if enemy_ship:
                predicted_thrust = self.enemy_thrust[enemy_ship.id]
                ex, ey = self.enemy_location[enemy_ship.id]
                next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
                if my_ship.laser and self.do_laser:
                    power = self.asses_laser_power(my_ship, thrust_action, enemy_ship)
                    if power > 0:
                        actions.append(my_ship.do_laser(ex, ey, power))

            enemy_ship = self.choose_explode_target(my_ship, thrust_action, enemy_ships)
            if enemy_ship:
                predicted_thrust = self.enemy_thrust[enemy_ship.id]
                next_dist = my_ship.next_dist(thrust_action, enemy_ship, predicted_thrust)
                if next_dist < 6 and st.me == ATACKER and self.T > 7 and len(my_ships) >= len(enemy_ships):
                    actions = [my_ship.do_explode()]
                if next_dist < 6 and st.me == DEFENDER and self.T > 7 and len(my_ships) > len(enemy_ships):
                    actions = [my_ship.do_explode()]
            all_actions_of_all_ships.extend(actions)
        return all_actions_of_all_ships
