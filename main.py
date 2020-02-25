import pygame
import os
import requests
from PIL import Image
import sys
from io import BytesIO
from get_delta import get_spn

pygame.init()


def initialize():
    global address, delta, coordinates, image
    address = 'Альметьевск'
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
        # "pt": f"{','.join([str(i) for i in coordinates])},pm2wtl",
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
        "l": map_types[now_type],
        # "pt": f"{','.join([str(i) for i in coordinates])},pm2wtl",
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


class Button(pygame.sprite.Sprite):
    def __init__(self, y, activated, text):
        super().__init__(buttons)
        self.text = text
        self.image = pygame.Surface([20, 20])
        self.image.set_colorkey((0, 0, 0))
        self.activated = activated
        self.colour = colours[self.activated]
        pygame.draw.circle(self.image, self.colour, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 5, y

    def update(self):
        self.colour = colours[self.activated]
        pygame.draw.circle(self.image, self.colour, (10, 10), 10)


def draw_text(text_y, texts):
    font = pygame.font.Font(None, 25)
    for i in range(len(texts)):
        text = font.render(texts[i], 1, (0, 200, 0))
        screen.blit(text, (30, text_y - 30 * i))


width, height = 450, 450
screen = pygame.display.set_mode((width, height))
buttons = pygame.sprite.Group()
clock = pygame.time.Clock()
running = True
image = None
address = None
delta = None
coordinates = None
now_type = 0
colours = [(150, 150, 150), (80, 80, 80)]
btn_txt = ['Схема', 'Спутник', 'Гибрид']
btn_types = {'Схема': 0,
             'Спутник': 1,
             'Гибрид': 2}
map_types = {0: 'map',
             1: 'sat',
             2: 'sat,skl'}
initialize()

for i in range(3):
    Button(425 - i * 30, 1, btn_txt[i]) if i == 0 else Button(425 - i * 30, 0, btn_txt[i])

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
            if event.key == pygame.K_DOWN and -80 < coordinates[1] - delta:
                coordinates[1] -= delta
            if event.key == pygame.K_UP and coordinates[1] + delta < 80:
                coordinates[1] += delta
            if event.key == pygame.K_LEFT and -180 < coordinates[0] - delta:
                coordinates[0] -= delta
            if event.key == pygame.K_RIGHT and coordinates[0] + delta < 180:
                coordinates[0] += delta
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in buttons:
                if btn.rect.collidepoint(event.pos):
                    btn.activated = 1
                    now_type = btn_types[btn.text]
                    for btn2 in buttons:
                        if btn2 != btn:
                            btn2.activated = 0

    load_map()
    buttons.update()
    screen.blit(image, (0, 0))
    buttons.draw(screen)
    draw_text(425, btn_txt)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
