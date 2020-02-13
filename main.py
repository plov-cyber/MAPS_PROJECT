import pygame
import os
import requests
from PIL import Image
import sys
from io import BytesIO
from get_delta import get_spn


def initialize():
    global address, delta, coordinates, image
    address = " ".join(sys.argv[1:])
    delta = get_spn(address)

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print('Ошибка!')
        exit(0)

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]

    coordinates = [float(i) for i in toponym["Point"]["pos"].split()]

    map_params = {
        "ll": ",".join([str(i) for i in coordinates]),
        "spn": f'{delta:.3f},{delta:.3f}',
        "l": "map",
        "pt": f"{','.join([str(i) for i in coordinates])},pm2wtl",
        'size': '450,450'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    if not response:
        print('Ошибка!')
        exit(0)

    im = Image.open(BytesIO(response.content))
    im.save('map.png')
    image = load_image('map.png')


def load_map():
    global image
    map_params = {
        "ll": ",".join([str(i) for i in coordinates]),
        "spn": f'{delta:.3f},{delta:.3f}',
        "l": "map",
        "pt": f"{','.join([str(i) for i in coordinates])},pm2wtl",
        'size': '450,450'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    if not response:
        print('Ошибка!')
        exit(0)

    im = Image.open(BytesIO(response.content))
    im.save('map.png')
    image = load_image('map.png')


def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


width, height = 450, 450
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
image = None
address = None
delta = None
coordinates = None
initialize()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_PAGEUP:
                if delta > 0.002:
                    delta *= 0.5
            elif event.key == pygame.K_PAGEDOWN:
                if delta < 10:
                    delta *= 1.5

    load_map()
    screen.blit(image, (0, 0))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
