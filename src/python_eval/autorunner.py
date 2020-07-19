from interaction import send2
from multiprocessing import Process
from parser import drawState, from_python

_, [p1, p2] = send2([1, 0])

def id_strategy(state):
    return []

def player(id, key, strategy):
    fake_state = from_python([6, [0, 10, -1, id, 0, 2, [], [], 4, [], [256, 1, [448, 1, 64], [16, 128], []], [], []], 9, []])
    send2([2, key, []])
    state = send2([3, key, [0, 0, 0, 1]])
    images = []
    while True:
        state = send2([4, key, strategy(state)])
        images.append(drawState(fake_state, from_python(state))[1])
        if state[1] == 2:
            print('done')
            break
    images[0].save(f'player{id}.gif', save_all=True, append_images=images[1:])
        

p1 = Process(target=player, args=p1 + [id_strategy])
p2 = Process(target=player, args=p2 + [id_strategy])
p1.start()
p2.start()
p1.join()
p2.join()
