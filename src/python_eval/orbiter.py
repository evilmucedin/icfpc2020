from orbit_util import trace_orbit, sign
import random

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