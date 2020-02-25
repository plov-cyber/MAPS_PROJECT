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

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": f'{delta:.3f},{delta:.3f}',
        "l": "map",
        "pt": f"{','.join(toponym_coodrinates)},pm2wtl",
        'size': '450,450'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    if not response:
        print('Ошибка!')
        exit(0)

    im = Image.open(BytesIO(response.content))
    im.save('map.png')


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


def update_map():
    global image
    load_map(address)
    image = load_image('map.png')


width, heigth = 450, 450
screen = pygame.display.set_mode((width, heigth))
clock = pygame.time.Clock()
running = True
address = " ".join(sys.argv[1:])
delta = get_spn(address)
load_map(address)
image = load_image('map.png')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_PAGEUP]:
            if delta > 0.001:
                delta *= 0.5
            update_map()
        elif keys[pygame.K_PAGEDOWN]:
            if delta < 10:
                delta *= 1.5
            update_map()
    screen.blit(image, (0, 0))
    pygame.display.flip()
    clock.tick(15)
pygame.quit()
