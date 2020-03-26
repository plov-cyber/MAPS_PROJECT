import sys
import requests
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from get_delta import get_spn
from lonlat_distance import lonlat_distance


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
        self.org_server = "http://search-maps.yandex.ru/v1/"
        self.delta = None
        self.full_address = ''
        self.postal_code = ''
        self.coordinates = None
        self.geo_params = None
        self.org_params = None
        self.map_params = None
        self.mark = None

        self.scheme.setChecked(True)
        self.map_type.setId(self.scheme, 2)
        self.map_type.setId(self.sat, 1)
        self.map_type.setId(self.hybrid, 0)
        self.map_type.buttonClicked[int].connect(self.change_map_type)

        self.search.clicked.connect(self.search_object)
        self.delete_mark.clicked.connect(self.delete_object)
        self.postalcode.stateChanged[int].connect(self.postal_code_view)

        self.load_map(new_address=True)

    def load_map(self, new_address=False):
        if new_address:
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
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            self.coordinates = list(map(float, toponym['Point']['pos'].split()))
            self.mark = ",".join(list(map(str, self.coordinates))) + ',flag'
            self.full_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            if 'postal_code' in toponym["metaDataProperty"]["GeocoderMetaData"]['Address']:
                self.postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]['Address']["postal_code"]
            self.postal_code_view(self.postalcode.isChecked())

        self.map_params = {
            "ll": ",".join(list(map(str, self.coordinates))),
            "spn": f'{self.delta:.3f},{self.delta:.3f}',
            "l": self.map_types[self.now_type],
            'pt': self.mark,
            'size': '450,450'
        }
        response = requests.get(self.map_server, params=self.map_params)
        if not response:
            print('Ошибка при запросе изображения!')
            exit(0)

        self.pixmap.loadFromData(response.content)
        self.image.setPixmap(self.pixmap)

    def postal_code_view(self, state):
        if state == 0:
            self.lbl_address.setText('Адрес: ' + self.full_address)
        else:
            self.lbl_address.setText('Адрес: ' + self.full_address + ' ' + self.postal_code)

    def change_map_type(self, id):
        self.now_type = id
        self.load_map()

    def search_object(self):
        new_address = self.obj_address.text()
        self.obj_address.clear()
        if new_address:
            self.address = new_address
            self.load_map(new_address=True)

    def delete_object(self):
        self.mark = None
        self.lbl_address.setText('Адрес: ')
        self.org.setText('Организация: ')
        self.full_address = ''
        self.postal_code = ''
        self.load_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.delta > 0.002:
                self.delta *= 0.5
        if event.key() == Qt.Key_PageDown:
            if self.delta < 10:
                self.delta *= 1.5
        if event.key() == Qt.Key_Down and -80 < self.coordinates[1] - self.delta:
            self.coordinates[1] -= self.delta / 2
        if event.key() == Qt.Key_Up and self.coordinates[1] + self.delta < 80:
            self.coordinates[1] += self.delta / 2
        if event.key() == Qt.Key_Left and -180 < self.coordinates[0] - self.delta:
            self.coordinates[0] -= self.delta
        if event.key() == Qt.Key_Right and self.coordinates[0] + self.delta < 180:
            self.coordinates[0] += self.delta
        self.load_map()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.coordinates[0] += ((event.x() - 225.5) / 225.5) * (self.delta / 2)
            self.coordinates[1] += ((225.5 - event.y()) / 225.5) * (self.delta / 2)
            self.find_address()
        elif event.button() == Qt.RightButton:
            self.coordinates[0] += ((event.x() - 225.5) / 225.5) * (self.delta / 2)
            self.coordinates[1] += ((225.5 - event.y()) / 225.5) * (self.delta / 2)
            self.find_organisation()
        self.load_map(new_address=True)

    def find_address(self):
        self.geo_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": ",".join(list(map(str, self.coordinates))),
            "format": "json"
        }
        response = requests.get(self.geo_server, params=self.geo_params)
        if not response:
            print('Ошибка при нахождении заданного адреса!')
            exit(0)

        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        self.address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

    def find_organisation(self):
        self.geo_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": ",".join(list(map(str, self.coordinates))),
            "format": "json"
        }
        response = requests.get(self.geo_server, params=self.geo_params)
        if not response:
            print('Ошибка при нахождении заданного адреса!')
            exit(0)

        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        search_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

        self.org_params = {
            "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
            "text": search_address,
            "lang": "ru_RU",
            # "ll": ",".join(list(map(str, self.coordinates))),
            "type": "biz"
        }

        response = requests.get(self.org_server, params=self.org_params)
        if not response:
            print('Ошибка при нахождении заданного адреса!')
            exit(0)

        json_response = response.json()
        org = json_response["features"]
        if org:
            org = org[0]
        else:
            print('Организаций не найдено!')

        self.address = org['properties']['CompanyMetaData']['address']
        org_name = org["properties"]["CompanyMetaData"]["name"]
        point = ','.join(str(i) for i in org["geometry"]["coordinates"])
        distance = int(lonlat_distance([float(i) for i in point.split(',')], self.coordinates))
        print(distance)
        if distance <= 50:
            self.org.setText('Организация: ' + org_name)
        else:
            self.org.setText('Организация: ')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    program = Map()
    program.show()
    sys.exit(app.exec())
