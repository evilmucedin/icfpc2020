import requests
import sys

from orbiter import orbiter_strategy
from interaction import send2

def player(key, strategy, server_url):
    send2([2, key, []], server_url=server_url)
    state = send2([3, key, [256, 5, 13, 1]], server_url=server_url)
    images = []
    while True:
        state = send2([4, key, strategy(state)], server_url=server_url)
        if state[1] == 2:
            print('done')
            break

def main():
    server_url = sys.argv[1]
    player_key = sys.argv[2]
    print('ServerUrl: %s; PlayerKey: %s' % (server_url, player_key))

    player(int(player_key), orbiter_strategy, server_url)


if __name__ == '__main__':
    main()