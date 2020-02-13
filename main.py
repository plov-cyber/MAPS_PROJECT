import pygame
import os
import requests
from PIL import Image
import sys
from io import BytesIO
from get_delta import get_spn


def load_map(toponym_to_find):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print('Ошибка!')
        exit(0)

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"].split()
    toponym_longitude, toponym_lattitude = toponym_coodrinates

    delta = get_spn(toponym_to_find)

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": delta,
        "l": "map",
        "pt": f"{','.join(toponym_coodrinates)},pm2wtl",
        'size': '450,450'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    im = Image.open(BytesIO(response.content))
    im.save('data/map.png')


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


width, heigth = 450, 450
screen = pygame.display.set_mode((width, heigth))
clock = pygame.time.Clock()
running = True
address = " ".join(sys.argv[1:])
load_map(address)
image = load_image('map.png')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(image, (0, 0))
    pygame.display.flip()
    clock.tick(15)
pygame.quit()
