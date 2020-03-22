import sys
import requests
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from get_delta import get_spn


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('map.ui', self)

        self.pixmap = QPixmap()
        self.address = 'Альметьевск'
        self.map_types = ['sat,skl', 'sat', 'map']
        self.now_type = 2
        self.geo_server = "http://geocode-maps.yandex.ru/1.x/"
        self.map_server = "http://static-maps.yandex.ru/1.x/"
        self.delta = None
        self.coordinates = None
        self.geo_params = None
        self.map_params = None

        self.scheme.setChecked(True)
        self.map_type.setId(self.scheme, 2)
        self.map_type.setId(self.sat, 1)
        self.map_type.setId(self.hybrid, 0)
        self.map_type.buttonClicked[int].connect(self.change_map_type)

        self.map_init()

    def map_init(self):
        self.delta = get_spn(self.address)
        self.geo_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.address,
            "format": "json"
        }

        response = requests.get(self.geo_server, params=self.geo_params)
        if not response:
            print('Ошибка при нахождении заданного адреса!')
            exit(0)

        json_response = response.json()
        self.coordinates = list(map(float, json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]['Point']['pos'].split()))

        self.map_params = {
            "ll": ",".join(list(map(str, self.coordinates))),
            "spn": f'{self.delta:.3f},{self.delta:.3f}',
            "l": "map",
            # "pt": f"{','.join([str(i) for i in coordinates])},pm2wtl",
            'size': '450,450'
        }
        response = requests.get(self.map_server, params=self.map_params)
        if not response:
            print('Ошибка при запросе изображения!')
            exit(0)

        self.pixmap.loadFromData(response.content)
        self.image.setPixmap(self.pixmap)

    def change_map_type(self, id):
        self.now_type = id
        self.load_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.delta > 0.002:
                self.delta *= 0.5
        if event.key() == Qt.Key_PageDown:
            if self.delta < 10:
                self.delta *= 1.5
        if event.key() == Qt.Key_Up and -80 < self.coordinates[1] - self.delta:
            self.coordinates[1] -= self.delta
        if event.key() == Qt.Key_Up and self.coordinates[1] + self.delta < 80:
            self.coordinates[1] += self.delta
        if event.key() == Qt.Key_Left and -180 < self.coordinates[0] - self.delta:
            self.coordinates[0] -= self.delta
        if event.key() == Qt.Key_Right and self.coordinates[0] + self.delta < 180:
            self.coordinates[0] += self.delta
        self.load_map()

    def load_map(self):
        self.map_params = {
            "ll": ",".join([str(i) for i in self.coordinates]),
            "spn": f'{self.delta:.3f},{self.delta:.3f}',
            "l": self.map_types[self.now_type],
            # "pt": f"{','.join([str(i) for i in coordinates])},pm2wtl",
            'size': '450,450'
        }

        response = requests.get(self.map_server, params=self.map_params)
        if not response:
            print('Ошибка при запросе изображения!')
            exit(0)

        self.pixmap.loadFromData(response.content)
        self.image.setPixmap(self.pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    program = Map()
    program.show()
    sys.exit(app.exec())
