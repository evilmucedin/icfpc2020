import requests
from modulate import modulate_anything, demodulate, to_str

API_KEY = '3bd205ec3d2640ac9b73eccecf9d540e'

def send(data):
    data = to_str(modulate_anything(data))
    response = requests.post(f'https://icfpc2020-api.testkontur.ru/aliens/send?apiKey={API_KEY}', data=data).text
    return demodulate(response)

if __name__ == "__main__":
    assert send(0) == [0]