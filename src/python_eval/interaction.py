import requests
from modulate import modulate_anything, demodulate, to_str

API_KEY = '3bd205ec3d2640ac9b73eccecf9d540e'

def sum_stats(stats):
    return stats[0] + 4*stats[1] + 12*stats[2] + 2*stats[3]

def print_player_info(pi):
    try:
        print(f'  PlayerInfoFull: {pi}')
        print(f'  Rounds: {pi[0]}')
        print(f'  My playerId: {pi[1]}')
        print(f'  Total number of stats (x1+4*x2+12*x3+2*x4), two constants?: {pi[2]}')
        print(f'  Unknown: {pi[3]}')
        print(f'  Starting ship params: {pi[4]} -> total {sum_stats(pi[4])}')
    except:
        pass

def print_game_state(gs):
    try:
        print(f'   GameStateFull: {gs}')
        print(f'   Unknown: {gs[0]}')
        print(f'   Unknown: {gs[1]}')
        for i, shipaction in enumerate(gs[2]):
            ship, actions = shipaction
            print(f'    ShipFull {i}: {ship}')
            print(f'    Ship {i} playerId: {ship[0]}')
            print(f'    Ship {i} shipId: {ship[1]}')
            print(f'    Ship {i} ship coordinates: {ship[2]}')
            print(f'    Ship {i} ship velocity - coord change: {ship[3]}')
            print(f'    Ship {i} stats: {ship[4]}')
            print(f'    Ship {i} unknown: {ship[5]}')
            print(f'    Ship {i} unknown: {ship[6]}')
            print(f'    Ship {i} unknown: {ship[7]}')
            print(f'    Ship {i} previous actions: {actions}')
    except:
        pass

def send(data):
    print(f'Sending {data}')
    if type(data) == list and len(data) == 3 and type(data[2]) == list:
        for k in range(len(data[2])):
            if type(data[2][k]) == list and len(data[2][k]) == 3:
                last = data[2][k][2] 
                if type(last) == list and len(last) == 2:
                    data[2][k][2] = tuple(data[2][k][2])
    print(f'Actually sending {data}')
    data = to_str(modulate_anything(data))
    response = requests.post(f'https://icfpc2020-api.testkontur.ru/aliens/send?apiKey={API_KEY}', data=data).text
    res = demodulate(response)
    print(f'Res: {res}')
    try:
        print(f'Const 1: {res[0]}, Game stage: {res[1]}')
        print_player_info(res[2])
        print_game_state(res[3])
    except:
        pass
    return res

if __name__ == "__main__":
    #assert send(0) == [0]
    send([4, 7364416995030719050, [[0, 0, (1, 1)]]])
