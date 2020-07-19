from orbit_util import trace_orbit, sign
import random
from states import ShipState, State, JoinResult

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

class OrbiterStrategy(object):
    def __init__(self, shoot, printships, duplicate):
        self.shoot = shoot
        self.printships = printships
        self.duplicate = duplicate
        self.T = 0
        self.birthday = {}

    def pick_stats(self, joinres):
        joinres = JoinResult.parse(joinres)
        las = 5
        regen = 13
        lives = 1
        fuel = joinres.budget - 4 * las - 12 * regen - 2 * lives
        return [fuel, las, regen, lives]

    def apply(self, state):
        self.T += 1
        st = State.parse(state)
        actions = []
        my_ships = []
        enemy_ships = []
        for some_ship in st.ships:
            if some_ship.state.id not in self.birthday:
                self.birthday[some_ship.state.id] = self.T
            if some_ship.state.player == st.me:
                my_ships.append(some_ship)
            else:
                enemy_ships.append(some_ship)
        if self.printships:
            print(f'T:{self.T} Player {st.me}: {" ".join(str([s.state.fuel, s.state.laser, s.state.regen, s.state.lives]) for s in my_ships)}')
        for my_ship in my_ships:
            birthday = self.birthday[my_ship.state.id]
            age = self.T - birthday
            if self.duplicate and my_ship.state.lives > 1 and self.T > 10:
                actions.append([3, my_ship.state.id, [my_ship.state.fuel // 2, my_ship.state.laser // 2, my_ship.state.regen // 2, my_ship.state.lives // 2]])
            my_pos = [my_ship.state.x, my_ship.state.y]
            my_vel = [my_ship.state.vx, my_ship.state.vy]
            cur_closest = trace_orbit(my_pos[0], my_pos[1], my_vel[0], my_vel[1])
            thrust = (0, 0)
            if cur_closest <= 17:
                thrust = (-sign(my_pos[0]), -sign(my_pos[0])) if abs(my_pos[0]) > abs(my_pos[1]) else (sign(my_pos[1]), -sign(my_pos[1]))

            # find closest friend - if too close randomize movement (include velocity in distance computation)
            closest_ship, dist = None, 1000
            for other in my_ships:
                if other.state.id == my_ship.state.id: continue
                od = abs(other.state.x - my_ship.state.x) + abs(other.state.y - my_ship.state.y) + abs(other.state.vx - my_ship.state.vx) + abs(other.state.vy - my_ship.state.vy)
                if od < dist:
                    dist = od
                    closest_ship = other
            if closest_ship and dist < 4:
                thrust = (random.randint(-1, 1), random.randint(-1, 1))

            actions.append([0, my_ship.state.id, thrust])
            if enemy_ships:
                enemy_ship = random.choice(enemy_ships)
                enemy_pos = [enemy_ship.state.x, enemy_ship.state.y]
                enemy_speed = [enemy_ship.state.vx, enemy_ship.state.vy]
                if self.shoot:
                    for my_ship in my_ships:
                        actions.append([2, my_ship.state.id, (enemy_pos[0] + enemy_speed[0], enemy_pos[1] + enemy_speed[1]), my_ship.state.laser])

        return actions
