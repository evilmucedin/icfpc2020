from interaction import send2
from multiprocessing import Process
from parser import drawState, from_python
import random

_, [p1, p2] = send2([1, 0])

def sign(x):
    return 1 if x > 0 else -1

def survivor_strategy(state):
    pid = state[2][1]
    actions = []
    my_ships = []
    enemy_ships = []
    for obj in state[3][2]:
        if obj[0][1] == pid:
            print(obj)
            my_ships.append(obj)
        else:
            enemy_ships.append(obj)
    for my_ship in my_ships:
        my_pos = my_ship[0][2]
        thrust = (sign(my_pos[0]), 0) if abs(my_pos[0]) > abs(my_pos[1]) else (0, sign(my_pos[1]))
        actions.append([0, my_ship[0][0], thrust])
        if enemy_ships:
            enemy_ship = random.choice(enemy_ships)
            enemy_pos = enemy_ship[0][2]
            enemy_speed = enemy_ship[0][3]
            actions.append([2, my_ship[0][0], (enemy_pos[0] + enemy_speed[0], enemy_pos[1] + enemy_speed[1]), 5])
    return actions

def player(id, key, strategy):
    fake_state = from_python([6, [0, 10, -1, id, 0, 2, [], [], 4, [], [256, 1, [448, 1, 64], [16, 128], []], [], []], 9, []])
    send2([2, key, []])
    state = send2([3, key, [256, 5, 13, 1]])
    images = []
    while True:
        state = send2([4, key, strategy(state)])
        images.append(drawState(fake_state, from_python(state))[1])
        if state[1] == 2:
            print('done')
            break
    images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])
        

p1 = Process(target=player, args=p1 + [survivor_strategy])
p2 = Process(target=player, args=p2 + [survivor_strategy])
p1.start()
p2.start()
p1.join()
p2.join()
