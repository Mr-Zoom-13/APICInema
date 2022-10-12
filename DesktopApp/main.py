import sys
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QDialog, QWidget, QApplication, \
    QPlainTextEdit, QMainWindow, QComboBox, QLabel, QCheckBox, QLCDNumber, QFrame, QWidget, \
    QGroupBox, QListWidget, QTabWidget, QFileDialog
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from PyQt5.QtGui import QPixmap, QColor
from collections import Counter
import csv
import os
from pathlib import Path
import random
import xlsxwriter
from PyQt5 import QtCore, QtMultimedia, QtGui
from main_form import Ui_MainWindow as MainWindowForm
from client_form import Ui_MainWindow as ClientForm
from admin_form import Ui_MainWindow as AdminForm
from dialog_form import Ui_Dialog as DialogForm
from dialog_exit_form import Ui_Dialog as DialogExitForm
from requests import get, post, delete, put
import urllib3

URL = "https://www.api-cinema.mr-zoom.com/api/v2/"
urllib3.disable_warnings()


class Client(QMainWindow, ClientForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # УСТАНОВКА ИКОНКИ
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setFixedWidth(1110)
        self.setFixedHeight(790)

        # ПОДКЛЮЧЕНИЕ К БД
        self.con = sqlite3.connect('baza.db')
        self.cur = self.con.cursor()

        # ПРОЯВЛЕНИЯ/ПОКАЗ
        self.combo_halls.hide()
        self.combo_sessions.hide()
        self.combo_time.hide()
        self.choose_btn.hide()
        self.pay.hide()
        self.price.hide()
        self.label_price.hide()

        # УСТАНОВКА АФИШЫ НАЧАЛЬНОЙ
        self.playbill = 0
        all_playbills = get(URL + 'playbills', verify=False).json()[
            'playbills']
        self.playbills_paths = []
        if all_playbills:
            if 'playbills' not in os.listdir(Path.cwd()):
                os.mkdir('playbills')
            os.chdir(str(Path.cwd()) + '\playbills')
            for i in all_playbills:
                self.playbills_paths.append(i['key_word'] + '.png')
                if i['key_word'] + '.png' not in os.listdir(Path.cwd()):
                    with open(i['key_word'] + '.png', 'wb') as image:
                        image.write(eval(i['image']))
            pixmap = QPixmap(self.playbills_paths[self.playbill])
            pixmap5 = pixmap.scaled(1111, 481)
            self.playbill_image.setPixmap(pixmap5)
            os.chdir('..')

        # ВСЕ ПОДКЛЮЧЕНИЯ
        self.right_image.clicked.connect(self.image_spin_right)
        self.left_image.clicked.connect(self.image_spin_left)
        self.clear_products.clicked.connect(self.clear_products_func)
        self.add_product.clicked.connect(self.pereme)
        self.pay_btn.clicked.connect(self.buy_snacks)
        self.pay.clicked.connect(self.pay_money)
        self.choose_btn.clicked.connect(self.buy_place)
        self.nearst_sessions.itemClicked.connect(self.nearst_buy)
        self.check_list.itemClicked.connect(self.del_snack)
        self.combo_cinema.currentTextChanged.connect(self.changed_cinema)
        self.combo_halls.currentTextChanged.connect(self.changed_hall)
        self.combo_sessions.currentTextChanged.connect(self.changed_session)
        self.combo_time.currentTextChanged.connect(self.changed_time)
        self.title_nearst.currentTextChanged.connect(self.find_nearst)
        self.exit_btn.clicked.connect(self.exit_btn_func)

        # ДОБАВЛЕНИЕ АЙТЕМОВ
        self.coca_cola_gramm.addItem('100мл')
        self.coca_cola_gramm.addItem('250мл')
        self.coca_cola_gramm.addItem('500мл')
        self.sprite_gramm.addItem('100мл')
        self.sprite_gramm.addItem('250мл')
        self.sprite_gramm.addItem('500мл')
        self.popcorn_sweet_gramm.addItem('100гр')
        self.popcorn_sweet_gramm.addItem('250гр')
        self.popcorn_sweet_gramm.addItem('500гр')
        self.popcorn_salt_gramm.addItem('100гр')
        self.popcorn_salt_gramm.addItem('250гр')
        self.popcorn_salt_gramm.addItem('500гр')

        # СООБЩЕНИЯ
        self.ERROR_NOT_NEARST = 'К сожалению сеансов на это кино нет!'
        self.ERROR_ZERO = 'Вы ничего не выбрали!'
        self.ERROR_MESSAGE = 'color: red;'
        self.SUCCESS_CHECK = 'Ваш чек успешно выгружен!'
        self.SUCCESS_MESSAGE = 'color: green;'

        # ВЫЗОВ ФУНКЦИЙ
        self.start()

        # ОСТАЛЬНОЕ
        self.nachos_with.setChecked(True)

        # НУЖНЫЕ ЛИСТЫ
        self.snacks = list()
        self.buy_seats_list = list()
        self.snacks_list = ['Попкорн(сладкий) -', 'Попкорн(соленый) -',
                            'Начос(150гр) без соуса - ', 'Газировка Coca-Cola -',
                            'Газировка Sprite -', 'Батончик Snickers -']
        self.add_snacks_spin = [self.popcorn_sweet_spin, self.popcorn_salt_spin,
                                self.nachos_spin, self.coca_cola_spin, self.sprite_spin,
                                self.snickers_spin]
        self.add_snacks_gramm = [self.popcorn_sweet_gramm, self.popcorn_salt_gramm, '',
                                 self.coca_cola_gramm, self.sprite_gramm, '']

        # НАПОЛНЕНИЕ БЛИЖАЙШИХ СЕАНСОВ
        all_sessions = get(URL + 'sessions', verify=False).json()[
            'sessions']
        self.title_nearst.addItem('')
        for session in all_sessions:
            self.title_nearst.addItem(session['title'])

        # УСТАНОВКА ЦЕНЫ
        all_prices = get(URL + 'prices', verify=False).json()['prices']
        this_price = 1
        for price in all_prices:
            if price['id'] == 1:
                this_price = price['price']
        self.ticket_price.setText(self.ticket_price.text() + str(this_price) + ' р.')

        # ОБОЗНАЧЕНИЯ МЕСТ
        d = QLabel(self.tab_2)
        d.resize(13, 13)
        pixmap = QPixmap('red_square.jpg')
        d.setPixmap(pixmap)
        d.move(860, 210)
        c = QLabel(self.tab_2)
        c.resize(14, 14)
        pixmap = QPixmap('non_checked.PNG')
        c.setPixmap(pixmap)
        c.move(860, 240)

        # ДИЗАЙН ВЫХОДА
        self.exit_btn.setStyleSheet('color: white; background-color: red')

        # СОЗДАНИЕ ДИАЛОГА
        self.dialog_exit = Dialog_exit()

        # ДИЗАААЙН
        self.tab.setStyleSheet('.QWidget {background-image: url(back_1.jpg);}')
        self.tab_2.setStyleSheet('.QWidget {background-image: url(back_1.jpg);}')
        self.tab_3.setStyleSheet('.QWidget {background-image: url(back_1.jpg);}')
        self.label_32.setStyleSheet('color: #FF7C00')
        self.label.setStyleSheet('color: #FFF')
        self.label_27.setStyleSheet('color: #FFF')
        self.label_28.setStyleSheet('color: #FFF')
        self.label_29.setStyleSheet('color: #FFF')

        self.choose_btn.setStyleSheet('background-color: #FF7C00;')
        self.pay.setStyleSheet('background-color: #FF7C00;')

        self.clear_products.setStyleSheet('background-color: #FF7C00;')
        self.add_product.setStyleSheet('background-color: #FF7C00;')
        self.pay_btn.setStyleSheet('background-color: #FF7C00;')

    def exit_func(self):
        self.exit_form = MyWidget()
        self.hide()
        self.exit_form.show()

    def exit_btn_func(self):
        self.dialog_exit.buttonBox.accepted.connect(self.exit_func)
        self.dialog_exit.show()

    def pereme(self):
        for i in range(len(self.add_snacks_spin)):
            spin_snack = self.add_snacks_spin[i]
            if int(spin_snack.text()):
                number = int(spin_snack.text())
                all_prices = get(URL + 'prices', verify=False).json()[
                    'prices']
                price = 1
                for j in all_prices:
                    if j['id'] == i + 2:
                        price = j['price']
                if i != 2 and i != 5:
                    item = self.snacks_list[i]
                    gramm = self.add_snacks_gramm[i].currentText()
                    if gramm == '100гр' or gramm == '100мл':
                        itog_price = round(number * 1.1 * price, 2)
                    elif gramm == '250гр' or gramm == '250мл':
                        itog_price = round(number * 2.25 * price, 2)
                    elif gramm == '500гр' or gramm == '500мл':
                        itog_price = round(number * 2.4 * price, 2)
                    item += gramm + ' - ' + str(number) + 'шт. - ' + str(itog_price) + 'р.'
                elif i == 2:
                    if self.nachos_without.isChecked():
                        itog_price = round(number * price, 2)
                        item = 'Начос(150гр) без соуса - ' + str(number) + 'шт. - ' + str(
                            itog_price) + 'р.'
                    else:
                        itog_price = round(number * price + 50, 2)
                        item = 'Начос(150гр) с соусом - ' + str(number) + 'шт. - ' + str(
                            itog_price) + 'р.'
                elif i == 5:
                    item = 'Батончик Snickers -'
                    itog_price = round(number * price, 2)
                    item += str(number) + 'шт. - ' + str(itog_price) + 'р.'
                self.check_list.addItem(item)
                self.summa_lcd.display(self.summa_lcd.value() + itog_price)
                spin_snack.setValue(0)
                self.snacks.append(item)

    def del_snack(self, item):
        del self.snacks[self.snacks.index(item.text())]
        self.check_list.takeItem(self.check_list.currentRow())
        self.summa_lcd.display(
            self.summa_lcd.value() - float(item.text().split(' - ')[-1].split('р.')[0]))

    def buy_snacks(self):
        if self.summa_lcd.value() == '0' or not self.summa_lcd.value():
            self.message_snack.setText(self.ERROR_ZERO)
            self.message_snack.setStyleSheet(self.ERROR_MESSAGE)
        else:
            self.buy_func(self.summa_lcd.value(), self.snacks, self.summa_lcd.value())
            self.snacks = list()
            self.summa_lcd.display(0)
            self.clear_products_func()
            self.message_snack.setText(self.SUCCESS_CHECK)
            self.message_snack.setStyleSheet(self.SUCCESS_MESSAGE)

    def clear_products_func(self):
        self.check_list.clear()
        self.snacks = []
        self.summa_lcd.display(0)

    def data_user(self, number_phone, fio=''):
        self.number_phone = number_phone
        if fio:
            self.fio = fio
        else:
            all_users = get(URL + 'users', verify=False).json()['users']
            for user in all_users:
                if user['number_phone'] == int(number_phone):
                    self.fio = user['fio']

    def start(self, value=''):
        self.combo_cinema.clear()
        all_cinemas = get(URL + 'cinemas', verify=False).json()[
            'cinemas']
        self.combo_cinema.addItem('')
        if value:
            self.combo_cinema.addItem(value)
            self.combo_cinema.setCurrentIndex(1)
        for i in all_cinemas:
            if i['title'] != value:
                self.combo_cinema.addItem(i['title'])

    def find_nearst(self, value):
        self.nearst_sessions.clear()
        if value:
            title_session = value
            all_sessions = get(URL + 'sessions', verify=False).json()[
                'sessions']
            sessions = []
            for i in all_sessions:
                if i['title'] == title_session:
                    sessions.append(i)
            dates = []
            dates_with_info = dict()
            for i in sessions:
                old_data = i['data'].split('-')[0]
                data = datetime.datetime.strptime(old_data, '%Y.%m.%d %H:%M')
                if data > datetime.datetime.now():
                    if str(data) not in dates_with_info.keys():
                        dates_with_info[str(data)] = str(
                            [[i['title'], i['cinema_id'], i['hall_id'], i['data']]])
                    else:
                        peremen = eval(dates_with_info[str(data)])
                        peremen.append([i['title'], i['cinema_id'], i['hall_id'], i['data']])
                        dates_with_info[str(data)] = str(peremen)
                    dates.append(data)
            dates = list(set(dates))
            dates.sort()
            count = 4
            schet = 0
            is_empty = True
            while count:
                if schet <= len(dates) - 1:
                    zapis = eval(dates_with_info[str(dates[schet])])
                    if count - len(zapis) < 0:
                        zapis = zapis[:abs(count - len(zapis))]
                        count = 0
                    else:
                        count -= len(zapis)
                    for i in zapis:
                        all_cinemas = get(URL + 'cinemas', verify=False).json()['cinemas']
                        for j in all_cinemas:
                            if j['id'] == i[1]:
                                cinema_title = j['title']
                                break
                        all_halls = get(URL + 'halls', verify=False).json()['halls']
                        for j in all_halls:
                            if j['id'] == i[2]:
                                number_hall = j['number']
                                break
                        strochka = 'Кинотеатр: ' + cinema_title + '; Зал: ' + str(
                            number_hall) + '; Дата: ' + str(i[3]) + '; Кино: ' + i[0]
                        self.nearst_sessions.addItem(strochka)
                        is_empty = False
                    schet += 1
                else:
                    break
            if is_empty:
                self.statusBar().showMessage(self.ERROR_NOT_NEARST)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)

    def nearst_buy(self, item):
        cur_index = self.tabWidget.currentIndex()
        self.tabWidget.setCurrentIndex(cur_index + 1)
        zapis = item.text()
        title = zapis.split('Кинотеатр: ')[1].split('; Зал: ')[0]
        hall_id = int(zapis.split('; Зал: ')[1].split('; Дата: ')[0])
        session = zapis.split('; Кино:')[1].strip()
        data_time = zapis.split('; Дата: ')[1].split('; Кино: ')[0]
        self.start(value=title)
        self.changed_cinema(value=title, now=hall_id)
        self.changed_hall(value=hall_id, now=session)
        self.changed_session(value=session, now=data_time)
        self.buy_place()

    def image_spin_right(self):
        if 'playbills' not in os.listdir(Path.cwd()):
            os.mkdir('playbills')
        os.chdir(str(Path.cwd()) + '\playbills')
        self.playbill += 1
        if self.playbill > len(self.playbills_paths) - 1:
            self.playbill = 0
        pixmap = QPixmap(self.playbills_paths[self.playbill])
        pixmap5 = pixmap.scaled(1111, 481)
        self.playbill_image.setPixmap(pixmap5)
        os.chdir('..')

    def image_spin_left(self):
        if 'playbills' not in os.listdir(Path.cwd()):
            os.mkdir('playbills')
        os.chdir(str(Path.cwd()) + '\playbills')
        self.playbill -= 1
        if self.playbill < 0:
            self.playbill = len(self.playbills_paths) - 1
        pixmap = QPixmap(self.playbills_paths[self.playbill])
        pixmap5 = pixmap.scaled(1111, 481)
        self.playbill_image.setPixmap(pixmap5)
        os.chdir('..')

    def changed_cinema(self, value, now=0):
        self.combo_halls.clear()
        self.clear_seats()
        self.combo_halls.clear()
        self.combo_sessions.clear()
        self.combo_sessions.hide()
        self.combo_time.clear()
        self.combo_time.hide()
        self.choose_btn.hide()
        self.label_price.hide()
        self.price.hide()
        self.price.display(0)
        self.pay.hide()
        if value:
            self.combo_halls.addItem('')
            if now:
                self.combo_halls.addItem(str(now))
                self.combo_halls.setCurrentIndex(1)
            all_cinemas = get(URL + 'cinemas', verify=False).json()[
                'cinemas']
            for i in all_cinemas:
                if i['title'] == self.combo_cinema.currentText():
                    id_cinema = i['id']
                    break
            all_halls = get(URL + 'halls', verify=False).json()['halls']
            halls = []
            for i in all_halls:
                if i['cinema_id'] == id_cinema:
                    halls.append(i)
            for i in halls:
                if str(i['number']) != str(now):
                    self.combo_halls.addItem(str(i['number']))
            self.combo_halls.show()
        else:
            self.combo_halls.hide()

    def changed_hall(self, value, now=''):
        self.combo_sessions.clear()
        self.clear_seats()
        self.combo_sessions.clear()
        self.combo_time.clear()
        self.combo_time.hide()
        self.choose_btn.hide()
        self.label_price.hide()
        self.price.hide()
        self.price.display(0)
        self.pay.hide()
        if value:
            self.combo_sessions.addItem('')
            if now:
                self.combo_sessions.addItem(now)
                self.combo_sessions.setCurrentIndex(1)

            all_cinemas = get(URL + 'cinemas', verify=False).json()[
                'cinemas']
            for i in all_cinemas:
                if i['title'] == self.combo_cinema.currentText():
                    id_cinema = i['id']
                    break
            all_halls = get(URL + 'halls', verify=False).json()['halls']
            for i in all_halls:
                if i['cinema_id'] == id_cinema and i['number'] == int(value):
                    id_hall = i['id']
                    break
            all_sessions = get(URL + 'sessions', verify=False).json()[
                'sessions']
            sessions = []
            for i in all_sessions:
                if i['cinema_id'] == id_cinema and i['hall_id'] == id_hall:
                    sessions.append(i)
            for i in self.check_old_data(sessions):
                if i != now:
                    self.combo_sessions.addItem(i)
            self.combo_sessions.show()
        else:
            self.combo_sessions.hide()

    def changed_session(self, value, now=''):
        self.combo_time.clear()
        self.clear_seats()
        self.combo_time.clear()
        self.choose_btn.hide()
        self.label_price.hide()
        self.price.hide()
        self.price.display(0)
        self.pay.hide()
        if value:
            self.combo_time.addItem('')
            if now:
                self.combo_time.addItem(now)
                self.combo_time.setCurrentIndex(1)
            all_cinemas = get(URL + 'cinemas', verify=False).json()['cinemas']
            for i in all_cinemas:
                if i['title'] == self.combo_cinema.currentText():
                    id_cinema = i['id']
                    break
            all_halls = get(URL + 'halls', verify=False).json()['halls']
            for i in all_halls:
                if i['cinema_id'] == id_cinema and i['number'] == int(
                        self.combo_halls.currentText()):
                    id_hall = i['id']
                    break
            all_sessions = get(URL + 'sessions', verify=False).json()[
                'sessions']
            times = []
            for i in all_sessions:
                if i['cinema_id'] == id_cinema and i['hall_id'] == id_hall and i[
                    'title'] == value:
                    times.append(i)
            for i in times:
                old_data = i['data'].split('-')[0]
                data = datetime.datetime.strptime(old_data, '%Y.%m.%d %H:%M')
                if data > datetime.datetime.now():
                    if i['data'] != now:
                        self.combo_time.addItem(i['data'])
            self.combo_time.show()
        else:
            self.combo_time.hide()

    def changed_time(self, value):
        self.clear_seats()
        self.label_price.hide()
        self.price.hide()
        self.price.display(0)
        self.pay.hide()
        if value:
            self.choose_btn.show()
        else:
            self.choose_btn.hide()

    def buy_place(self):
        self.pay.show()
        self.price.show()
        self.label_price.show()
        all_cinemas = get(URL + 'cinemas', verify=False).json()['cinemas']
        for i in all_cinemas:
            if i['title'] == self.combo_cinema.currentText():
                id_cinema = i['id']
                break
        all_halls = get(URL + 'halls', verify=False).json()['halls']
        for i in all_halls:
            if i['cinema_id'] == id_cinema and i['number'] == int(
                    self.combo_halls.currentText()):
                id_hall = i['id']
                break
        all_sessions = get(URL + 'sessions', verify=False).json()['sessions']
        for i in all_sessions:
            if i['title'] == self.combo_sessions.currentText() and i['cinema_id'] == id_cinema\
                    and i['hall_id'] == id_hall:
                self.seats = eval(i['seats'])
                break
        count_x = 70
        count_y = 95
        for i in range(len(self.seats)):
            for j in range(len(self.seats[i])):
                if self.seats[i][j] == 1:
                    d = QLabel(self.tab_2)
                    d.resize(13, 13)
                    pixmap = QPixmap('red_square.jpg')
                    d.setPixmap(pixmap)
                    d.move(count_x, count_y)
                else:
                    d = QCheckBox(self.tab_2)
                    d.clicked.connect(self.changed_seat)
                    d.move(count_x, count_y)
                count_x += 22
                d.show()
            count_x = 70
            count_y += 21

    def changed_seat(self):
        x = int((self.sender().geometry().x() - 70) / 22)
        y = int((self.sender().geometry().y() - 95) / 21)
        all_prices = get(URL + 'prices', verify=False).json()['prices']
        for i in all_prices:
            if i['id'] == 1:
                price = float(i['price'])
                break
        item = 'Билет на ' + str(y + 1) + ' ряд место ' + str(x + 1) + ' - ' + str(
            price) + ' р.'
        if self.sender().isChecked():
            self.seats[y][x] = 1
            self.price.display(self.price.value() + price)
            self.buy_seats_list.append(item)
        else:
            self.seats[y][x] = 0
            self.price.display(self.price.value() - price)
            del self.buy_seats_list[self.buy_seats_list.index(item)]

    def pay_money(self):
        if self.price.value() == '0' or not self.price.value():
            self.statusBar().showMessage(self.ERROR_ZERO)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        else:
            all_cinemas = get(URL + 'cinemas', verify=False).json()['cinemas']
            for i in all_cinemas:
                if i['title'] == self.combo_cinema.currentText():
                    id_cinema = i['id']
                    break
            all_halls = get(URL + 'halls', verify=False).json()['halls']
            for i in all_halls:
                if i['cinema_id'] == id_cinema and i['number'] == int(
                        self.combo_halls.currentText()):
                    id_hall = i['id']
                    break
            all_sessions = get(URL + 'sessions', verify=False).json()[
                'sessions']
            for i in all_sessions:
                if i['title'] == self.combo_sessions.currentText() and i[
                    'cinema_id'] == id_cinema and i['hall_id'] == id_hall and i[
                    'data'] == self.combo_time.currentText():
                    id_session = i['id']
                    break
            print(
                put(URL + f'sessions/{id_session}', verify=False, json={
                    'seats': str(self.seats)
                }).json())
            self.buy_func(self.price.value(), self.buy_seats_list, self.price.value())
            self.buy_seats_list = list()
            self.buy_place()
            self.price.display(0)
            self.statusBar().showMessage(self.SUCCESS_CHECK)
            self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)

    def clear_seats(self):
        d = QLabel(self.tab_2)
        d.resize(780, 800)
        pixmap = QPixmap('white.jpg')
        d.setPixmap(pixmap)
        d.move(70, 90)
        d.show()

    def buy_func(self, summa, items, itog_sum):
        if 'output' not in os.listdir(Path.cwd()):
            os.mkdir('output')
        os.chdir(str(Path.cwd()) + '\output')
        current_title = self.make_new_data(
            str(datetime.datetime.now().year)) + '.' + self.make_new_data(
            str(datetime.datetime.now().month)) + '.' + self.make_new_data(
            str(datetime.datetime.now().day)) + ' ' + self.make_new_data(
            str(datetime.datetime.now().hour)) + '.' + self.make_new_data(
            str(datetime.datetime.now().minute)) + '.txt'
        current = 1
        while True:
            if current_title in os.listdir(Path.cwd()):
                if '(' in current_title:
                    current_title = current_title.split(').txt')[0][:-1] + str(
                        current) + ').txt'
                else:
                    current_title = current_title.split('.txt')[0] + '(' + str(
                        current) + ').txt'
                current += 1
            else:
                break
        individual_number = ''
        while not individual_number:
            part_1 = random.randint(1, 9)
            part_2 = random.randint(1, 9)
            part_3 = random.randint(1, 9)
            part_4 = random.randint(1, 9)
            part_5 = random.randint(1, 9)
            part_6 = random.randint(1, 9)
            individual_number = int(
                str(part_1) + str(part_2) + str(part_3) + str(part_4) + str(part_5) + str(
                    part_6))
            all_logs = get(URL + 'logs', verify=False).json()['logs']
            for i in all_logs:
                if i['checks'] == individual_number:
                    individual_number = ''
                    break
        data_now = str(datetime.datetime.now())
        all_users = get(URL + 'users', verify=False).json()['users']
        for i in all_users:
            if i['number_phone'] == self.number_phone:
                user_id = i['id']
                break
        post(URL + 'logs', verify=False, json={
            'user_id': user_id, 'summa': summa, 'checks': individual_number
        }).json()
        file = open(current_title, 'w', encoding='utf8')
        file.write('Чек Сети Кинотеатров\n')
        file.write('--------------------\n')
        for i in items:
            file.write(i + '\n')
        file.write('--------------------\n')
        file.write('Итого: ' + str(itog_sum) + ' р.\n\n')
        file.write('УНИКАЛЬНЫЙ ИДЕНТИФИКАТОР ЧЕКА: ' + str(individual_number))
        file.close()
        os.chdir(str(Path.cwd()).split('\output')[0])
        os.system('explorer ' + os.getcwd() + "\output\\" + current_title)

    def make_new_data(self, data):
        if len(data) == 1:
            data = '0' + data
        return data

    def check_old_data(self, sessions):
        itog = list()
        for j in sessions:
            old_data = j['data'].split('-')[0]
            data = datetime.datetime.strptime(old_data, '%Y.%m.%d %H:%M')
            if data > datetime.datetime.now():
                itog.append(j['title'])
        return itog


class Dialog(QDialog, DialogForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # УСТАНОВКА ИКОНКИ
        self.setWindowIcon(QtGui.QIcon('icon.png'))


class Dialog_exit(QDialog, DialogExitForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # УСТАНОВКА ИКОНКИ
        self.setWindowIcon(QtGui.QIcon('icon.png'))


class Admin(QMainWindow, AdminForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # УСТАНОВКА ИКОНКИ
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setFixedWidth(795)
        self.setFixedHeight(660)

        # ПОДКЛЮЧЕНИЕ К БД
        self.con = sqlite3.connect('baza.db')
        self.cur = self.con.cursor()

        # ВСЕ ПОДКЛЮЧЕНИЯ
        self.add_cinema.clicked.connect(self.add_cinema_func)
        self.add_hall.clicked.connect(self.add_hall_func)
        self.add_session.clicked.connect(self.add_session_func)
        self.add_playbill.clicked.connect(self.add_playbill_func)
        self.del_playbill.clicked.connect(self.del_playbill_func)
        self.upload_btn.clicked.connect(self.upload_func)
        self.check_btn.clicked.connect(self.check_func)
        self.ticket_btn.clicked.connect(self.change_func)
        self.popcorn_sweet_btn.clicked.connect(self.change_func)
        self.popcorn_salt_btn.clicked.connect(self.change_func)
        self.nachos_btn.clicked.connect(self.change_func)
        self.cola_btn.clicked.connect(self.change_func)
        self.sprite_btn.clicked.connect(self.change_func)
        self.snickers_btn.clicked.connect(self.change_func)
        self.report_btn.clicked.connect(self.report_func)
        self.exit_btn.clicked.connect(self.exit_btn_func)

        # СООБЩЕНИЯ
        self.statusBar().setStyleSheet('font-size: 20px;')
        self.ERROR_INCORRECT_DATA = 'Некорректные данные!'
        self.ERROR_EMPTY_FIELD = 'Пустое поле!'
        self.ERROR_CINEMA_ALREADY_CREATED = 'Кинотеатр с таким названием уже есть!'
        self.ERROR_NOT_EXIST_CINEMA = 'Кинотеатра с данным названием не существует!'
        self.ERROR_PAST_DATE = 'Указана прошедшая дата!'
        self.ERROR_KEY_WORD_ALREADY = 'Такой ключ уже существует!'
        self.ERROR_NOT_KEY = 'Афиши с таким ключом нет!'
        self.ERROR_CHECK = 'Чек поддельный!'
        self.ERROR_DATA_ALREADY = 'В это время уже есть сеанс кино!'
        self.ERROR_NOT_PATH = 'Вы не указали картинку афиши!'
        self.SUCCESS_ADD_CINEMA = 'Новый кинотеатр успешно добавлен!'
        self.SUCCESS_ADD_HALL = 'Новый зал в кинотеатр успешно добавлен!'
        self.SUCCESS_ADD_SESSION = 'Новый сеанс кино успешно добавлен!'
        self.SUCCESS_ADD_PLAYBILL = 'Новая афиша успешно добавлена!'
        self.SUCCESS_DEL_PLAYBILL = 'Афиша успешно удалена!'
        self.SUCCESS_UPDATE_PRICE = 'Цена успешно обновлена!'
        self.SUCCESS_UPLOAD = 'Чеки успешно выгружены!'
        self.SUCCESS_CHECK = 'Чек верный!'
        self.SUCCESS_UPDATE_PRICES_SNACKS = 'Цена успешно обновлена!'
        self.SUCCESS_UPLOAD_REPORT = 'Отчет по доходам успешно выгружен!'
        self.ERROR_MESSAGE = 'font-size: 20px; color: red;'
        self.SUCCESS_MESSAGE = 'font-size: 20px; color: green;'

        # НУЖНЫЕ ЛИСТЫ
        self.snacks_prices = [120, 220, 310, 400, 490, 580, 670]
        self.new_prices = [self.ticket, self.popcorn_sweet, self.popcorn_salt, self.nachos,
                           self.cola, self.sprite, self.snickers]

        # ДИЗАЙН ВЫХОДА
        self.exit_btn.setStyleSheet('color: white; background-color: red')

        # СОЗДАНИЕ ДИАЛОГА
        self.dialog = Dialog()
        self.dialog_exit = Dialog_exit()

        # ВЫЗОВ ФУНКЦИЙ
        self.update_playbill_func()
        self.update_info()

        # ДИЗАЙН
        self.tab.setStyleSheet('.QWidget {background-image: url(back_2.jpg);}')
        self.tab_3.setStyleSheet('background-color: #3e9aff;')
        self.tab_2.setStyleSheet('.QWidget {background-image: url(back_2.jpg);}')
        self.label_13.setStyleSheet('color: #FF7C00')

        self.add_cinema.setStyleSheet('background-color: #FF7C00;')
        self.add_hall.setStyleSheet('background-color: #FF7C00;')
        self.add_session.setStyleSheet('background-color: #FF7C00;')
        self.add_playbill.setStyleSheet('background-color: #FF7C00;')
        self.del_playbill.setStyleSheet('background-color: #FF7C00;')
        self.upload_btn.setStyleSheet('background-color: #FF7C00;')
        self.check_btn.setStyleSheet('background-color: #FF7C00;')
        self.report_btn.setStyleSheet('background-color: #FF7C00;')

        self.ticket_btn.setStyleSheet('background-color: #FF7C00;')
        self.popcorn_sweet_btn.setStyleSheet('background-color: #FF7C00;')
        self.popcorn_salt_btn.setStyleSheet('background-color: #FF7C00;')
        self.nachos_btn.setStyleSheet('background-color: #FF7C00;')
        self.cola_btn.setStyleSheet('background-color: #FF7C00;')
        self.sprite_btn.setStyleSheet('background-color: #FF7C00;')
        self.snickers_btn.setStyleSheet('background-color: #FF7C00;')

    def create_new_rgb(self):
        while True:
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            new_color = (red, green, blue)
            if new_color not in self.colors:
                self.colors.append(new_color)
                return new_color

    def update_info(self):
        self.colors = list()
        self.colors_with_info = dict()
        self.table_cinema.clear()
        self.table_hall.clear()
        self.table_session.clear()

        # КИНОТЕАТРЫ
        title = ['ID', 'Название']
        self.table_cinema.setColumnCount(len(title))
        self.table_cinema.setHorizontalHeaderLabels(title)
        all_cinemas = get(URL + 'cinemas', verify=False).json()[
            'cinemas']
        for i, row in enumerate(all_cinemas):
            color = self.create_new_rgb()
            self.colors_with_info[row['title']] = color
            self.table_cinema.setRowCount(
                self.table_cinema.rowCount() + 1)
            for j, item in enumerate(row.keys()):
                self.table_cinema.setItem(i, j, QTableWidgetItem(str(row[item])))
                self.table_cinema.item(i, j).setBackground(QColor(*color))
            self.table_cinema.setRowCount(i + 1)
        self.table_cinema.resizeColumnsToContents()

        # ЗАЛЫ
        all_halls = get(URL + 'halls', verify=False).json()['halls']
        title = ['ID', 'Размер в ширину', 'Размер в длину', 'Кинотеатр', 'Номер зала']
        keys_halls = ['id', 'width', 'height', 'cinema_id', 'number']
        self.table_hall.setColumnCount(len(title))
        self.table_hall.setHorizontalHeaderLabels(title)
        self.table_hall.setRowCount(0)
        for i, row in enumerate(all_halls):
            color = self.create_new_rgb()
            self.colors_with_info[str(row['id'])] = color
            self.table_hall.setRowCount(
                self.table_hall.rowCount() + 1)
            for j, item in enumerate(keys_halls):
                if j == 3:
                    for k in all_cinemas:
                        if k['id'] == row[item]:
                            title_cinema = k['title']
                            break
                    self.table_hall.setItem(i, j, QTableWidgetItem(title_cinema))
                    self.table_hall.item(i, j).setBackground(
                        QColor(*self.colors_with_info[title_cinema]))
                else:
                    self.table_hall.setItem(i, j, QTableWidgetItem(str(row[item])))
                if not j or j == 4:
                    self.table_hall.item(i, j).setBackground(QColor(*color))
        self.table_hall.resizeColumnsToContents()

        # СЕССИИ
        all_sessions, fullable = self.check_old_data(
            get(URL + 'sessions', verify=False).json()['sessions'])
        title = ['ID', 'Название', 'Кинотеатр', 'Номер зала', 'Дата', 'Полная посадка']
        keys_sessions = ['id', 'title', 'cinema_id', 'hall_id', 'data', 'seats']
        self.table_session.setColumnCount(len(title))
        self.table_session.setHorizontalHeaderLabels(title)
        self.table_session.setRowCount(0)
        color_no = self.create_new_rgb()
        color_yes = self.create_new_rgb()
        for i, row in enumerate(all_sessions):
            color = self.create_new_rgb()
            self.table_session.setRowCount(
                self.table_session.rowCount() + 1)
            for j, item in enumerate(keys_sessions):
                if j == 2:
                    for k in all_cinemas:
                        if k['id'] == row[item]:
                            title_cinema = k['title']
                            break
                    self.table_session.setItem(i, j, QTableWidgetItem(title_cinema))
                    self.table_session.item(i, j).setBackground(
                        QColor(*self.colors_with_info[title_cinema]))
                elif j == 3:
                    for k in all_halls:
                        if k['id'] == row[item]:
                            number_hall = k['number']
                            break
                    self.table_session.setItem(i, j, QTableWidgetItem(str(number_hall)))
                    self.table_session.item(i, j).setBackground(
                        QColor(*self.colors_with_info[str(row[item])]))
                else:
                    self.table_session.setItem(i, j, QTableWidgetItem(str(row[item])))
                if j == 1:
                    if row[item] not in self.colors_with_info.keys():
                        self.table_session.item(i, j).setBackground(QColor(*color))
                        self.colors_with_info[row['title']] = color
                    else:
                        self.table_session.item(i, j).setBackground(
                            QColor(*self.colors_with_info[row[item]]))
            if fullable[i]:
                self.table_session.setItem(i, j + 1, QTableWidgetItem('Да'))
                self.table_session.item(i, j + 1).setBackground(QColor(*color_yes))
            else:
                self.table_session.setItem(i, j, QTableWidgetItem('Нет'))
                self.table_session.item(i, j).setBackground(QColor(*color_no))
        self.table_session.resizeColumnsToContents()

    def exit_func(self):
        self.exit_form = MyWidget()
        self.hide()
        self.exit_form.show()

    def exit_btn_func(self):
        self.dialog_exit.buttonBox.accepted.connect(self.exit_func)
        self.dialog_exit.show()

    def make_report(self):
        os.chdir(str(Path.cwd()) + '\output')
        title = self.report.text()
        all_checks = get(URL + 'logs', verify=False).json()['logs']
        months = {'01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
                  '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
                  '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}
        income = {'Январь': 0, 'Февраль': 0, 'Март': 0, 'Апрель': 0, 'Май': 0, 'Июнь': 0,
                  'Июль': 0, 'Август': 0, 'Сентябрь': 0, 'Октябрь': 0, 'Ноябрь': 0,
                  'Декабрь': 0}
        for i in all_checks:
            data = i['data']
            summa = i['summa']
            month_number = data.split('-')[1]
            month = months[month_number]
            income[month] += summa
        itog = list()
        for i in income.keys():
            itog.append((i, income[i]))
        workbook = xlsxwriter.Workbook(title)
        worksheet = workbook.add_worksheet()
        for row, (item, price) in enumerate(itog):
            worksheet.write(row, 0, item)
            worksheet.write(row, 1, price)
            chart = workbook.add_chart({'type': 'pie'})
            chart.add_series({'values': '=Sheet1!B1:B12'})
            worksheet.insert_chart('C1', chart)
            chart.add_series({
                'categories': '=Sheet1!$A$1:$A$12',
                'values': '=Sheet1!$B$1:$B$12',
            })
        workbook.close()
        os.chdir(str(Path.cwd()).split('\output')[0])
        os.system('explorer ' + os.getcwd() + "\output\\" + title)
        self.statusBar().showMessage(self.SUCCESS_UPLOAD_REPORT)
        self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)

    def report_func(self):
        title = self.report.text()
        if '.xlsx' not in title:
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
        else:
            if 'output' not in os.listdir(Path.cwd()):
                os.mkdir('output')
            os.chdir(str(Path.cwd()) + '\output')
            if title in os.listdir(Path.cwd()):
                os.chdir(str(Path.cwd()).split('\output')[0])
                self.dialog.buttonBox.accepted.connect(self.make_report)
                self.dialog.show()
            elif not title:
                os.chdir(str(Path.cwd()).split('\output')[0])
                self.statusBar().showMessage(self.ERROR_EMPTY_FIELD)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            else:
                os.chdir(str(Path.cwd()).split('\output')[0])
                self.make_report()

    def change_func(self):
        id_item = self.snacks_prices.index(self.sender().geometry().y())
        try:
            new_price = int(self.new_prices[id_item].text())
        except ValueError:
            self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        else:
            if abs(new_price) != new_price:
                self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            else:
                put(URL + f'prices/{id_item + 1}', verify=False, json={
                    'price': new_price
                }).json()
                self.statusBar().showMessage(self.SUCCESS_UPDATE_PRICES_SNACKS)
                self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
                self.new_prices[id_item].clear()

    def check_func(self):
        individual_number = self.check.text()
        if not individual_number:
            self.statusBar().showMessage(self.ERROR_EMPTY_FIELD)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        elif self.letters(individual_number):
            self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        else:
            all_logs = get(URL + 'logs', verify=False).json()['logs']
            checking = False
            for i in all_logs:
                if i['checks'] == int(individual_number):
                    checking = True
                    break
            if checking:
                self.statusBar().showMessage(self.SUCCESS_CHECK)
                self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
                self.check.clear()
            else:
                self.statusBar().showMessage(self.ERROR_CHECK)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)

    def upload(self):
        title = self.csv_title.text()
        if title:
            if '\output' not in str(Path.cwd()):
                os.chdir(str(Path.cwd()) + '\output')
            with open(title, 'w', encoding='utf8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['id', 'fio', 'number_phone', 'summa', 'check', 'data'])
                all_logs = get(URL + 'logs', verify=False).json()['logs']
                all_users = get(URL + 'users', verify=False).json()[
                    'users']
                for log in all_logs:
                    for i in all_users:
                        if i['id'] == log['user_id']:
                            writer.writerow(
                                [log['id'], i['fio'], i['number_phone'], log['summa'],
                                 log['checks'], log['data']])
                            break
                self.statusBar().showMessage(self.SUCCESS_UPLOAD)
                self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
                self.csv_title.clear()
            os.chdir(str(Path.cwd()).split('\output')[0])
            os.system('explorer ' + os.getcwd() + "\output\\" + title)

    def upload_func(self):
        title = self.csv_title.text()
        if '.csv' not in title:
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
        else:
            if 'output' not in os.listdir(Path.cwd()):
                os.mkdir('output')
            os.chdir(str(Path.cwd()) + '\output')
            if not title:
                os.chdir(str(Path.cwd()).split('\output')[0])
                self.statusBar().showMessage(self.ERROR_EMPTY_FIELD)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            elif title in os.listdir(Path.cwd()):
                os.chdir(str(Path.cwd()).split('\output')[0])
                self.dialog.buttonBox.accepted.connect(self.upload)
                self.dialog.show()
            else:
                os.chdir(str(Path.cwd()).split('\output')[0])
                self.upload()

    def update_playbill_func(self):
        self.key_word_del.clear()
        all_playbills = get(URL + 'playbills', verify=False).json()[
            'playbills']
        for i in all_playbills:
            self.key_word_del.addItem(i['key_word'])

    def del_playbill_func(self):
        key_word = self.key_word_del.currentText()
        all_playbills = get(URL + 'playbills', verify=False).json()[
            'playbills']
        for i in all_playbills:
            if i['key_word'] == key_word:
                delete(URL + f'playbills/{i["id"]}', verify=False)
                break
        self.statusBar().showMessage(self.SUCCESS_DEL_PLAYBILL)
        self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
        self.update_playbill_func()

    def add_playbill_func(self):
        path = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        with open(path, 'rb') as image:
            blob_data = image.read()
        if not path:
            self.statusBar().showMessage(self.ERROR_NOT_PATH)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        else:
            key_word = self.key_word.text()
            is_in_key_words = False
            all_playbills = get(URL + 'playbills', verify=False).json()[
                'playbills']
            for i in all_playbills:
                if i['key_word'] == key_word:
                    is_in_key_words = True
            if not key_word:
                self.statusBar().showMessage(self.ERROR_EMPTY_FIELD)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            elif is_in_key_words:
                self.statusBar().showMessage(self.ERROR_KEY_WORD_ALREADY)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            else:
                print(post(URL + 'playbills', verify=False, json={
                    'image': str(blob_data), 'key_word': key_word
                }))
                self.statusBar().showMessage(self.SUCCESS_ADD_PLAYBILL)
                self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
                self.key_word.clear()
                self.update_playbill_func()

    def add_cinema_func(self):
        title_new_cinema = self.title_new_cinema.text()
        title_already = False
        all_cinemas = get(URL + 'cinemas', verify=False).json()[
            'cinemas']
        for i in all_cinemas:
            if i['title'] == title_new_cinema:
                title_already = True
        if not title_new_cinema:
            self.statusBar().showMessage(self.ERROR_EMPTY_FIELD)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        elif title_already:
            self.statusBar().showMessage(self.ERROR_CINEMA_ALREADY_CREATED)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        else:
            print(post(URL + 'cinemas', verify=False, json={
                'title': title_new_cinema
            }).json())
            self.statusBar().showMessage(self.SUCCESS_ADD_CINEMA)
            self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
            self.title_new_cinema.setText('')
            self.update_info()

    def add_hall_func(self):
        title_cinema = self.name_cinema_hall.text()
        length_hall = self.length_hall.text()
        width_hall = self.width_hall.text()
        if not title_cinema or not length_hall or not width_hall:
            self.statusBar().showMessage(self.ERROR_EMPTY_FIELD)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        elif self.letters(length_hall) or self.letters(width_hall) or abs(
                int(length_hall)) != int(length_hall) or abs(int(width_hall)) != int(
            width_hall):
            self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        elif int(length_hall) > 30 or int(width_hall) > 35:
            self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        else:
            first_request = get(URL + 'cinemas', verify=False).json()
            cinema_id = None
            for i in first_request['cinemas']:
                if i['title'] == title_cinema:
                    cinema_id = i['id']
            if cinema_id:
                all_halls = get(URL + 'halls', verify=False).json()[
                    'halls']
                max_number = 0
                for i in all_halls:
                    if i['cinema_id'] == cinema_id and i['number'] > max_number:
                        max_number = i['number']
                request = post(URL + 'halls', verify=False, json={
                    'width': width_hall, 'height': length_hall, 'cinema_id': cinema_id,
                    'number': max_number + 1
                }).json()
                print(request)
                self.statusBar().showMessage(self.SUCCESS_ADD_HALL)
                self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
                self.name_cinema_hall.setText('')
                self.length_hall.setText('')
                self.width_hall.setText('')
                self.update_info()
            else:
                self.statusBar().showMessage(self.ERROR_NOT_EXIST_CINEMA)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)

    def add_session_func(self):
        title_cinema = self.title_cinema_session.text()
        number_hall = self.number_hall_session.text()
        title = self.title_session.text()
        data = self.time_session.text()
        data_figures = Counter(data)
        flag_incorect_data = False
        try:
            first_data = data.split('-')[0]
            second_data = str(data.split('-')[0])[:-5] + str(data.split('-')[1])
            data_current = datetime.datetime.strptime(first_data, '%Y.%m.%d %H:%M')
            data_current_2 = datetime.datetime.strptime(second_data, '%Y.%m.%d %H:%M')
        except Exception:
            self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
            self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
        else:
            if not title_cinema or not number_hall or not title or not data:
                self.statusBar().showMessage(self.ERROR_EMPTY_FIELD)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            elif self.letters(number_hall) or (
                    data_figures[' '] != 1 or data_figures['.'] != 2 or data_figures[
                ':'] != 2 or data_figures['-'] != 1):
                self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            elif data_current <= datetime.datetime.now():
                self.statusBar().showMessage(self.ERROR_PAST_DATE)
                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
            else:
                try:
                    all_cinemas = get(URL + 'cinemas', verify=False).json()[
                            'cinemas']
                    for i in all_cinemas:
                        if i['title'] == title_cinema:
                            id_cinema = i['id']
                            break
                    all_halls = get(URL + 'halls', verify=False).json()['halls']
                    hall = None
                    for i in all_halls:
                        if i['number'] == int(number_hall) and i['cinema_id'] == id_cinema:
                            hall = i
                            break
                    if hall:
                        id_hall = hall['id']
                        length_hall = hall['height']
                        width_hall = hall['width']
                        all_sessions = \
                            get(URL + 'sessions', verify=False).json()['sessions']
                        sessions = []
                        for i in all_sessions:
                            if i['cinema_id'] == id_cinema and i['hall_id'] == id_hall:
                                sessions.append(i)
                        for i in sessions:
                            first_data = i['data'].split('-')[0]
                            second_data = str(i['data'].split('-')[0])[:-5] + str(
                                i['data'].split('-')[1])
                            data_check = datetime.datetime.strptime(first_data,
                                                                    '%Y.%m.%d %H:%M')
                            data_check_2 = datetime.datetime.strptime(second_data,
                                                                      '%Y.%m.%d %H:%M')
                            if (
                                    data_current >= data_check and data_current <= data_check_2) or (
                                    data_current_2 >= data_check and data_current_2 <= data_check_2):
                                self.statusBar().showMessage(self.ERROR_DATA_ALREADY)
                                self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
                                flag_incorect_data = True
                        if not flag_incorect_data:
                            seats = list()
                            for i in range(length_hall):
                                seats.append([])
                                for j in range(width_hall):
                                    seats[-1].append(0)
                            seats = str(seats)
                            post(URL + 'sessions', verify=False, json={
                                'title': title, 'cinema_id': id_cinema, 'hall_id': id_hall,
                                'data': data,
                                'seats': seats
                            }).json()
                            self.statusBar().showMessage(self.SUCCESS_ADD_SESSION)
                            self.statusBar().setStyleSheet(self.SUCCESS_MESSAGE)
                            self.title_cinema_session.setText('')
                            self.number_hall_session.setText('')
                            self.title_session.setText('')
                            self.time_session.setText('')
                            self.update_info()
                    else:
                        self.statusBar().showMessage(self.ERROR_INCORRECT_DATA)
                        self.statusBar().setStyleSheet(self.ERROR_MESSAGE)
                except TypeError:
                    self.statusBar().showMessage(self.ERROR_NOT_EXIST_CINEMA)
                    self.statusBar().setStyleSheet(self.ERROR_MESSAGE)

    def letters(self, text):
        try:
            text = int(text)
            return False
        except ValueError:
            return True

    def check_old_data(self, sessions):
        itog = list()
        fullable = list()
        for j in sessions:
            old_data = j['data'].split('-')[0]
            data = datetime.datetime.strptime(old_data, '%Y.%m.%d %H:%M')
            if data > datetime.datetime.now():
                is_full = True
                for i in eval(j['seats']):
                    for k in i:
                        if not k:
                            is_full = False
                itog.append(j)
                fullable.append(is_full)
        return itog, fullable


class MyWidget(QMainWindow, MainWindowForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # УСТАНОВКА ИКОНКИ
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setFixedWidth(795)
        self.setFixedHeight(660)

        # ПОДКЛЮЧЕНИЕ К БД
        self.con = sqlite3.connect('baza.db')
        self.cur = self.con.cursor()

        # МЕЛОДИЯ ЗАГРУЗКИ
        media = QtCore.QUrl.fromLocalFile('1.mp3')
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)
        self.player.play()

        # ПОДКЛЮЧЕНИЯ
        self.auth.clicked.connect(self.authtorization)
        self.reg.clicked.connect(self.open_registration)
        self.authorization_btn.clicked.connect(self.open_authorization)
        self.registration_btn.clicked.connect(self.registration)

        # ВЫЗОВ ФУНКЦИЯ И СОЗДАНИЕ КЛАССОВ
        self.open_authorization()
        self.client_form = Client()
        self.admin_form = Admin()

        # СООБЩЕНИЯ
        self.ERROR_INCORRECT_DATA_NOT_REGISTRED = 'Введены некорректные данные либо же данный пользователь не зарегистрирован'
        self.ERROR_INCORRECT_DATA = 'Введены некорректные данные!'
        self.ERROR_USER_ALREADY_REGISTRED = 'Пользователь с данным номером телефона уже зарегистрирован!'

        # ДИЗАААЙН
        self.setStyleSheet('.QWidget {background-image: url(itog_back.jpg);}')
        self.label_7.setStyleSheet('color: #FF7C00')
        self.label_5.setStyleSheet('color: #FF7C00')

        self.registration_btn.setStyleSheet('background-color: #FF7C00;')
        self.authorization_btn.setStyleSheet('background-color: #FF7C00;')
        self.reg.setStyleSheet('background-color: #FF7C00;')
        self.auth.setStyleSheet('background-color: #FF7C00;')

    def authtorization(self):
        number_phone = self.input_number.text()
        password = self.input_password.text()
        users = get(URL + 'users', verify=False).json()['users']
        for i in users:
            if i['number_phone'] == int(number_phone):
                if check_password_hash(i['password'], password):
                    if i['is_admin']:
                        self.admin_form.show()
                    else:
                        self.client_form.data_user(int(number_phone))
                        self.client_form.show()
                    self.hide()
        self.label_3.setText(self.ERROR_INCORRECT_DATA_NOT_REGISTRED)

    def open_registration(self):
        self.label.show()
        self.input_fio.show()
        self.admin.show()
        self.client.show()
        self.label_7.show()
        self.label_5.hide()
        self.authorization_btn.show()
        self.registration_btn.show()
        self.auth.hide()
        self.client.setChecked(True)
        self.label_3.setText('')

    def open_authorization(self):
        self.label.hide()
        self.input_fio.hide()
        self.admin.hide()
        self.client.hide()
        self.label_7.hide()
        self.authorization_btn.hide()
        self.registration_btn.hide()
        self.auth.show()
        self.label_5.show()
        self.label_3.setText('')

    def registration(self):
        number_phone = self.input_number.text()
        fio = self.input_fio.text()
        flag_figures_in_fio = False
        for i in fio:
            if i.isdigit():
                flag_figures_in_fio = True
        if (not self.input_password.text() or not fio) or len(number_phone) != 11 or \
                number_phone[0] != '8' or flag_figures_in_fio:
            self.label_3.setText(self.ERROR_INCORRECT_DATA)
        else:
            password = generate_password_hash(self.input_password.text())
            is_admin = False
            if self.letters(number_phone):
                self.label_3.setText(self.ERROR_INCORRECT_DATA)
            else:
                if self.admin.isChecked():
                    is_admin = True
                is_registred_phone = False
                users = get(URL + 'users', verify=False).json()['users']
                for i in users:
                    if i['number_phone'] == int(number_phone):
                        is_registred_phone = True
                if is_registred_phone:
                    self.label_3.setText(self.ERROR_USER_ALREADY_REGISTRED)
                else:
                    number_phone = int(number_phone)
                    print(number_phone)
                    print(post(URL + 'users', verify=False,
                               json={'fio': fio, 'password': password,
                                     'number_phone': number_phone, 'is_admin': is_admin
                                     }).json())
                    if is_admin:
                        self.admin_form.show()
                    else:
                        self.client_form.data_user(int(number_phone), fio=fio)
                        self.client_form.show()
                    self.hide()

    def letters(self, text):
        try:
            text = int(text)
            return False
        except ValueError:
            return True


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
