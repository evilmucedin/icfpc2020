import requests
import sys

from swarmer import SwarmerStrategy
from orbiter import OrbiterStrategy
from interaction import send2

def player(key, strategy, sender):
    res = sender([2, key, [103652820, 192496425430]])
    initial_stats = strategy.pick_stats(res)
    state = sender([3, key, initial_stats])
    images = []
    while True:
        state = sender([4, key, strategy.apply(state)])
        if state[1] == 2:
            print('done')
            break

def main():
    server_url = sys.argv[1]
    player_key = sys.argv[2]
    print('ServerUrl: %s; PlayerKey: %s' % (server_url, player_key))
    sender = lambda msg: send2(msg, server_url=server_url)
    # strategy = OrbiterStrategy(do_laser=True, printships=False, duplicate=True)
    strategy = SwarmerStrategy()
    player(int(player_key), strategy, sender=sender)


if __name__ == '__main__':
    main()
