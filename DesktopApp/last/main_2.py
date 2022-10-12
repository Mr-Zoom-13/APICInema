import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QWidget, QApplication, QPlainTextEdit, QMainWindow, QComboBox, QLabel, QCheckBox, QLCDNumber, QFrame, QWidget, QGroupBox, QListWidget, QTabWidget, QFileDialog
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from PyQt5.QtGui import QPixmap
from collections import Counter
import csv
import os
from pathlib import Path
import random
import xlsxwriter


class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('client3.ui', self)
        self.con = sqlite3.connect('baza.db')
        self.cur = self.con.cursor()
        self.combo_halls.hide()
        self.combo_sessions.hide()
        self.combo_time.hide()
        self.start()
        self.combo_cinema.currentTextChanged.connect(self.changed_cinema)
        self.combo_halls.currentTextChanged.connect(self.changed_hall)
        self.combo_sessions.currentTextChanged.connect(self.changed_session)
        self.combo_time.currentTextChanged.connect(self.changed_time)
        self.choose_btn.clicked.connect(self.buy_place)
        self.choose_btn.hide()
        self.pay.hide()
        self.price.hide()
        self.label_price.hide()
        self.pay.clicked.connect(self.pay_money)
        self.playbill = 0
        playbills = self.cur.execute('SELECT * FROM Playbills').fetchall()
        pixmap = QPixmap(playbills[self.playbill][1])
        pixmap5 = pixmap.scaled(1111, 481)
        self.playbill_image.setPixmap(pixmap5)
        self.right_image.clicked.connect(self.image_spin_right)
        self.left_image.clicked.connect(self.image_spin_left)
        self.nearst_sessions.itemClicked.connect(self.nearst_buy)
        self.nearst_btn.clicked.connect(self.find_nearst)
        self.clear_products.clicked.connect(self.clear_products_func)
        self.add_product.clicked.connect(self.pereme)
        self.popcorn_sweet_gramm.addItem('100гр')
        self.popcorn_sweet_gramm.addItem('250гр')
        self.popcorn_sweet_gramm.addItem('500гр')
        self.popcorn_salt_gramm.addItem('100гр')
        self.popcorn_salt_gramm.addItem('250гр')
        self.popcorn_salt_gramm.addItem('500гр')
        self.nachos_with.setChecked(True)
        self.coca_cola_gramm.addItem('100мл')
        self.coca_cola_gramm.addItem('250мл')
        self.coca_cola_gramm.addItem('500мл')
        self.sprite_gramm.addItem('100мл')
        self.sprite_gramm.addItem('250мл')
        self.sprite_gramm.addItem('500мл')
        self.pay_btn.clicked.connect(self.buy_snacks)
        self.snacks = list()
        self.buy_seats_list = list()
        self.check_list.itemClicked.connect(self.del_snack)
        self.error_zero = 'Вы ничего не выбрали!'
        self.error_message = 'color: red;'
        self.success_check = 'Ваш чек успешно выгружен!'
        self.success_message = 'color: green;'
        self.snacks_list = ['Попкорн(сладкий) -', 'Попкорн(соленый) -', 'Начос(150гр) без соуса - ', 'Газировка Coca-Cola -', 'Газировка Sprite -', 'Батончик Snickers -']
        self.add_snacks_spin = [self.popcorn_sweet_spin, self.popcorn_salt_spin, self.nachos_spin, self.coca_cola_spin, self.sprite_spin, self.snickers_spin]
        self.add_snacks_gramm = [self.popcorn_sweet_gramm, self.popcorn_salt_gramm, '', self.coca_cola_gramm, self.sprite_gramm, '']

    def pereme(self):
        for i in range(len(self.add_snacks_spin)):
            spin_snack = self.add_snacks_spin[i]
            if int(spin_snack.text()):
                number = int(spin_snack.text())
                price = int(self.cur.execute('SELECT * FROM Prices WHERE id = ?', (i + 1,)).fetchone()[1])
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
        self.summa_lcd.display(self.summa_lcd.value() - float(item.text().split(' - ')[-1].split('р.')[0]))

    def buy_snacks(self):
        if self.summa_lcd.value() == '0' or not self.summa_lcd.value():
            self.message_snack.setText(self.error_zero)
            self.message_snack.setStyleSheet(self.error_message)
        else:
            self.buy_func(self.summa_lcd.value(), self.snacks, self.summa_lcd.value())
            self.snacks = list()
            self.summa_lcd.display(0)
            self.clear_products_func()
            self.message_snack.setText(self.success_check)
            self.message_snack.setStyleSheet(self.success_message)

    def clear_products_func(self):
        self.check_list.clear()
        self.summa_lcd.display(0)

    def data_user(self, number_phone, fio=''):
        self.number_phone = number_phone
        if fio:
            self.fio = fio
        else:
            self.fio = self.cur.execute('SELECT * FROM Users where number_phone = ?', (self.number_phone,)).fetchone()[1]

    def start(self, value=''):
        self.combo_cinema.clear()
        cinema = self.cur.execute('SELECT * FROM Cinema').fetchall()
        self.combo_cinema.addItem('')
        if value:
            self.combo_cinema.addItem(value)
            self.combo_cinema.setCurrentIndex(1)
        for i in cinema:
            if i[1] != value:
                self.combo_cinema.addItem(i[1])

    def find_nearst(self):
        self.nearst_sessions.clear()
        title_session = self.title.text()
        sessions = self.cur.execute('SELECT * FROM Sessions WHERE title = ?', (title_session,)).fetchall()
        dates = []
        dates_with_info = dict()
        for i in sessions:
            old_data = i[4].split('-')[0]
            data = datetime.datetime.strptime(old_data, '%Y.%m.%d %H:%M')
            if data > datetime.datetime.now():
                if str(data) not in dates_with_info.keys():
                    dates_with_info[str(data)] = str([i])
                else:
                    peremen = eval(dates_with_info[str(data)])
                    peremen.append(i)
                    dates_with_info[str(data)] = str(peremen)
                dates.append(data)
        dates = list(set(dates))
        dates.sort()
        count = 4
        schet = 0
        while count:
            if schet <= len(dates) - 1:
                zapis = eval(dates_with_info[str(dates[schet])])
                if count - len(zapis) < 0:
                    zapis = zapis[:abs(count - len(zapis))]
                    count = 0
                else:
                    count -= len(zapis)
                for i in zapis:
                    cinema_title = \
                    self.cur.execute('SELECT * FROM Cinema WHERE id = ?', (i[2],)).fetchone()[1]
                    number_hall = self.cur.execute('SELECT * FROM Halls WHERE id = ?', (int(i[3]),)).fetchone()[4]
                    strochka = 'Кинотеатр: ' + cinema_title + '; Зал: ' + str(
                        number_hall) + '; Дата: ' + str(i[4]) + '; Кино: ' + i[1]
                    self.nearst_sessions.addItem(strochka)
                schet += 1
            else:
                break

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
        self.playbill += 1
        playbills = self.cur.execute('SELECT * FROM Playbills').fetchall()
        if self.playbill > len(playbills) - 1:
            self.playbill = 0
        pixmap = QPixmap(playbills[self.playbill][1])
        pixmap5 = pixmap.scaled(1111, 481)
        self.playbill_image.setPixmap(pixmap5)

    def image_spin_left(self):
        self.playbill -= 1
        playbills = self.cur.execute('SELECT * FROM Playbills').fetchall()
        if self.playbill < 0:
            self.playbill = len(playbills) - 1
        pixmap = QPixmap(playbills[self.playbill][1])
        pixmap5 = pixmap.scaled(1111, 481)
        self.playbill_image.setPixmap(pixmap5)

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
            id_cinema = self.cur.execute('SELECT * FROM Cinema WHERE title = ?',
                                         (self.combo_cinema.currentText(),)).fetchone()[0]
            halls = self.cur.execute('SELECT * FROM Halls WHERE cinema = ?', (id_cinema,)).fetchall()
            for i in halls:
                if str(i[4]) != str(now):
                    self.combo_halls.addItem(str(i[4]))
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
            id_cinema = self.cur.execute('SELECT * FROM Cinema WHERE title = ?', (self.combo_cinema.currentText(),)).fetchone()[0]
            id_hall = self.cur.execute('SELECT * FROM Halls WHERE number = ? AND cinema = ?', (value, id_cinema)).fetchone()[0]
            sessions = self.cur.execute('SELECT * FROM Sessions WHERE cinema_id = ? AND hall_id = ?', (int(id_cinema), id_hall)).fetchall()
            itog = list()
            for j in sessions:
                old_data = j[4].split('-')[0]
                data = datetime.datetime.strptime(old_data, '%Y.%m.%d %H:%M')
                if data > datetime.datetime.now():
                    itog.append(j[1])
            itog = list(set(itog))
            for i in itog:
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
            id_cinema = self.cur.execute('SELECT * FROM Cinema WHERE title = ?',
                                         (self.combo_cinema.currentText(),)).fetchone()[0]
            id_hall = self.cur.execute('SELECT * FROM Halls WHERE number = ? AND cinema = ?', (self.combo_halls.currentText(), id_cinema)).fetchone()[0]
            times = self.cur.execute('SELECT * FROM Sessions WHERE title = ? AND cinema_id = ? AND hall_id = ?', (value, id_cinema, id_hall)).fetchall()
            for i in times:
                old_data = i[4].split('-')[0]
                data = datetime.datetime.strptime(old_data, '%Y.%m.%d %H:%M')
                if data > datetime.datetime.now():
                    if i[4] != now:
                        self.combo_time.addItem(i[4])
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
        id_cinema = self.cur.execute('SELECT * FROM Cinema WHERE title = ?',
                                     (self.combo_cinema.currentText(),)).fetchone()[0]
        id_hall = self.cur.execute('SELECT * FROM Halls WHERE number = ? AND cinema = ?',
                                   (self.combo_halls.currentText(), id_cinema)).fetchone()[0]
        self.seats = eval(self.cur.execute(
            'SELECT * FROM Sessions WHERE title = ? AND cinema_id = ? AND hall_id = ? AND data = ?',
            (self.combo_sessions.currentText(), id_cinema, id_hall, self.combo_time.currentText())).fetchone()[5])
        count_x = 70
        count_y = 95
        for i in range(len(self.seats)):
            for j in range(len(self.seats[i])):
                if self.seats[i][j] == 1:
                    d = QLabel(self.tab_2)
                    d.resize(13, 13)
                    pixmap = QPixmap('11.jpg')
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
        price = float(self.cur.execute('SELECT * FROM Prices where id= 0').fetchone()[1])
        item = 'Билет на ' + str(y + 1) + ' ряд место ' + str(x + 1) + ' - ' + str(price) + ' р.'
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
            self.statusBar().showMessage(self.error_zero)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            id_cinema = self.cur.execute('SELECT * FROM Cinema WHERE title = ?',
                                         (self.combo_cinema.currentText(),)).fetchone()[0]
            id_hall = self.cur.execute('SELECT * FROM Halls WHERE number = ? AND cinema = ?',
                                       (self.combo_halls.currentText(), id_cinema)).fetchone()[0]
            self.cur.execute('UPDATE Sessions SET seats = ? WHERE cinema_id = ? AND hall_id = ? AND data = ? AND title = ?', (str(self.seats), id_cinema, id_hall, self.combo_time.currentText(), self.combo_sessions.currentText()))
            self.con.commit()
            self.buy_func(self.price.value(), self.buy_seats_list, self.price.value())
            self.buy_seats_list = list()
            self.buy_place()
            self.price.display(0)
            self.statusBar().showMessage(self.success_check)
            self.statusBar().setStyleSheet(self.success_message)

    def clear_seats(self):
        d = QLabel(self.tab_2)
        d.resize(900, 900)
        pixmap = QPixmap('white.jpg')
        d.setPixmap(pixmap)
        d.move(70, 90)
        d.show()

    def buy_func(self, summa, items, itog_sum):
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
            checked_number = self.cur.execute('SELECT * FROM Logs WHERE checks = ?',
                                              (individual_number,)).fetchone()
            if checked_number:
                individual_number = ''
        data_now = str(datetime.datetime.now())
        self.cur.execute('INSERT INTO Logs(fio, number_phone, summa, checks, data) VALUES (?, ?, ?, ?, ?)', (self.fio, self.number_phone, summa, individual_number, data_now))
        self.con.commit()
        file = open('check.txt', 'w', encoding='utf8')
        file.write('Чек Сети Кинотеатров\n')
        file.write('--------------------\n')
        for i in items:
            file.write(i + '\n')
        file.write('--------------------\n')
        file.write('Итого: ' + str(itog_sum) + '.р\n\n')
        file.write('УНИКАЛЬНЫЙ ИДЕНТИФИКАТОР ЧЕКА: ' + str(individual_number))


class Dialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('dialog.ui', self)


class Admin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('admin2.ui', self)
        self.con = sqlite3.connect('baza.db')
        self.cur = self.con.cursor()
        self.statusBar().setStyleSheet('font-size: 20px;')
        self.add_cinema.clicked.connect(self.add_cinema_func)
        self.add_hall.clicked.connect(self.add_hall_func)
        self.add_session.clicked.connect(self.add_session_func)
        self.error_incorrect_data = 'Некорректные данные!'
        self.error_empty_field = 'Пустое поле!'
        self.error_cinema_alredy_created = 'Кинотеатр с таким названием уже есть!'
        self.error_not_exist_cinema = 'Кинотеатра с данным названием не существует!'
        self.error_past_date = 'Указана прошедшая дата!'
        self.error_key_word_already = 'Такой ключ уже существует!'
        self.error_not_key = 'Афиши с таким ключом нет!'
        self.error_check = 'Чек поддельный!'
        self.error_data_already = 'В это время уже есть сеанс кино!'
        self.error_not_path = 'Вы не указали картинку афиши!'
        self.success_add_cinema = 'Новый кинотеатр успешно добавлен!'
        self.success_add_hall = 'Новый зал в кинотеатр успешно добавлен!'
        self.success_add_session = 'Новый сеанс кино успешно добавлен!'
        self.success_add_playbill = 'Новая афиша успешно добавлена!'
        self.success_del_playbill = 'Афиша успешно удалена!'
        self.success_update_price = 'Цена успешно обновлена!'
        self.success_upload = 'Чеки успешно выгружены!'
        self.success_check = 'Чек верный!'
        self.success_update_prices_snacks = 'Цена успешно обновлена!'
        self.success_upload_report = 'Отчет по доходам успешно выгружен!'
        self.error_message = 'font-size: 20px; color: red;'
        self.success_message = 'font-size: 20px; color: green;'
        # self.new_price_btn.clicked.connect(self.update_price)
        self.add_playbill.clicked.connect(self.add_playbill_func)
        self.del_playbill.clicked.connect(self.del_playbill_func)
        self.upload_btn.clicked.connect(self.upload_func)
        self.dialog = Dialog()

        self.check_btn.clicked.connect(self.check_func)
        self.ticket_btn.clicked.connect(self.change_func)
        self.popcorn_sweet_btn.clicked.connect(self.change_func)
        self.popcorn_salt_btn.clicked.connect(self.change_func)
        self.nachos_btn.clicked.connect(self.change_func)
        self.cola_btn.clicked.connect(self.change_func)
        self.sprite_btn.clicked.connect(self.change_func)
        self.snickers_btn.clicked.connect(self.change_func)
        self.snacks_prices = [120, 220, 310, 400, 490, 580, 670]
        self.new_prices = [self.ticket, self.popcorn_sweet, self.popcorn_salt, self.nachos, self.cola, self.sprite, self.snickers]
        self.report_btn.clicked.connect(self.report_func)

    def make_report(self):
        title = self.report.text()
        all_checks = self.cur.execute('SELECT * FROM Logs').fetchall()
        months = {'01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
                  '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
                  '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}
        income = {'Январь': 0, 'Февраль': 0, 'Март': 0, 'Апрель': 0, 'Май': 0, 'Июнь': 0,
                  'Июль': 0, 'Август': 0, 'Сентябрь': 0, 'Октябрь': 0, 'Ноябрь': 0,
                  'Декабрь': 0}
        for i in all_checks:
            data = i[5]
            summa = int(i[3])
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
        self.statusBar().showMessage(self.success_upload_report)
        self.statusBar().setStyleSheet(self.success_message)

    def report_func(self):
        title = self.report.text()
        if title in os.listdir(Path.cwd()):
            self.dialog.buttonBox.accepted.connect(self.make_report)
            self.dialog.show()
        elif not title:
            self.statusBar().showMessage(self.error_empty_field)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            self.make_report()

    def change_func(self):
        id_item = self.snacks_prices.index(self.sender().geometry().y())
        try:
            new_price = int(self.new_prices[id_item].text())
        except ValueError:
            self.statusBar().showMessage(self.error_incorrect_data)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            if abs(new_price) != new_price:
                self.statusBar().showMessage(self.error_incorrect_data)
                self.statusBar().setStyleSheet(self.error_message)
            else:
                self.cur.execute('UPDATE Prices SET price = ? WHERE id = ?', (new_price, id_item))
                self.con.commit()
                self.statusBar().showMessage(self.success_update_prices_snacks)
                self.statusBar().setStyleSheet(self.success_message)
                self.new_prices[id_item].clear()

    def check_func(self):
        individual_number = self.check.text()
        if not individual_number:
            self.statusBar().showMessage(self.error_empty_field)
            self.statusBar().setStyleSheet(self.error_message)
        elif self.letters(individual_number):
            self.statusBar().showMessage(self.error_incorrect_data)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            checking = self.cur.execute('SELECT * FROM Logs WHERE checks = ?', (individual_number,)).fetchone()
            if checking:
                self.statusBar().showMessage(self.success_check)
                self.statusBar().setStyleSheet(self.success_message)
                self.check.clear()
            else:
                self.statusBar().showMessage(self.error_check)
                self.statusBar().setStyleSheet(self.error_message)

    def upload(self):
        title = self.csv_title.text()
        with open(title, 'w', encoding='utf8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['id', 'fio', 'number_phone', 'summa', 'check', 'data'])
            logs = self.cur.execute('SELECT * FROM Logs').fetchall()
            for i in logs:
                writer.writerow(i)
            self.statusBar().showMessage(self.success_upload)
            self.statusBar().setStyleSheet(self.success_message)
            self.csv_title.clear()

    def upload_func(self):
        title = self.csv_title.text()
        if not title:
            self.statusBar().showMessage(self.error_empty_field)
            self.statusBar().setStyleSheet(self.error_message)
        elif title in os.listdir(Path.cwd()):
            self.dialog.buttonBox.accepted.connect(self.upload)
            self.dialog.show()
        else:
            self.upload()

    def del_playbill_func(self):
        key_word = self.key_word_del.text()
        is_available = self.cur.execute('SELECT * FROM Playbills WHERE key_word = ?', (key_word,)).fetchone()
        if not key_word:
            self.statusBar().showMessage(self.error_empty_field)
            self.statusBar().setStyleSheet(self.error_message)
        elif not is_available:
            self.statusBar().showMessage(self.error_not_key)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            self.cur.execute('DELETE FROM Playbills where key_word = ?', (key_word,))
            self.con.commit()
            self.statusBar().showMessage(self.success_del_playbill)
            self.statusBar().setStyleSheet(self.success_message)
            self.key_word_del.clear()

    def add_playbill_func(self):
        path = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        if not path:
            self.statusBar().showMessage(self.error_not_path)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            key_word = self.key_word.text()
            is_in_key_words = self.cur.execute('SELECT * from Playbills WHERE key_word = ?', (key_word,)).fetchone()
            if not key_word:
                self.statusBar().showMessage(self.error_empty_field)
                self.statusBar().setStyleSheet(self.error_message)
            elif is_in_key_words:
                self.statusBar().showMessage(self.error_key_word_already)
                self.statusBar().setStyleSheet(self.error_message)
            else:
                self.cur.execute('INSERT INTO Playbills(file_path, key_word) VALUES (?, ?)', (path, key_word))
                self.con.commit()
                self.statusBar().showMessage(self.success_add_playbill)
                self.statusBar().setStyleSheet(self.success_message)
                self.key_word.clear()

    def add_cinema_func(self):
        title_new_cinema = self.title_new_cinema.text()
        titles = self.cur.execute('SELECT * from Cinema WHERE title = ?', (title_new_cinema,)).fetchone()
        if not title_new_cinema:
            self.statusBar().showMessage(self.error_empty_field)
            self.statusBar().setStyleSheet(self.error_message)
        elif titles:
            self.statusBar().showMessage(self.error_cinema_alredy_created)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            self.cur.execute('INSERT INTO Cinema(title) VALUES (?)', (title_new_cinema,))
            self.con.commit()
            self.statusBar().showMessage(self.success_add_cinema)
            self.statusBar().setStyleSheet(self.success_message)
            self.title_new_cinema.setText('')

    def add_hall_func(self):
        title_cinema = self.name_cinema_hall.text()
        length_hall = self.length_hall.text()
        width_hall = self.width_hall.text()
        if not title_cinema or not length_hall or not width_hall:
            self.statusBar().showMessage(self.error_empty_field)
            self.statusBar().setStyleSheet(self.error_message)
        elif self.letters(length_hall) or self.letters(width_hall) or abs(int(length_hall)) != int(length_hall) or abs(int(width_hall)) != int(width_hall):
            self.statusBar().showMessage(self.error_incorrect_data)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            try:
                id_cinema = self.cur.execute('SELECT * from Cinema WHERE title = ?', (title_cinema,)).fetchone()[0]
                try:
                    new_number = self.cur.execute(
                        'SELECT number FROM Halls WHERE cinema = ? ORDER BY number DESC LIMIT 1',
                        (id_cinema,)).fetchone()[
                                     0] + 1
                except TypeError:
                    new_number = 1
                self.cur.execute('INSERT INTO Halls(x, y, cinema, number) VALUES (?, ?, ?, ?)',
                                 (width_hall, length_hall, id_cinema, new_number))
                self.con.commit()
                self.statusBar().showMessage(self.success_add_hall)
                self.statusBar().setStyleSheet(self.success_message)
                self.name_cinema_hall.setText('')
                self.length_hall.setText('')
                self.width_hall.setText('')
            except TypeError:
                self.statusBar().showMessage(self.error_not_exist_cinema)
                self.statusBar().setStyleSheet(self.error_message)

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
            self.statusBar().showMessage(self.error_incorrect_data)
            self.statusBar().setStyleSheet(self.error_message)
        else:
            if not title_cinema or not number_hall or not title or not data:
                self.statusBar().showMessage(self.error_empty_field)
                self.statusBar().setStyleSheet(self.error_message)
            elif self.letters(number_hall) or (data_figures[' '] != 1 or data_figures['.'] != 2 or data_figures[':'] != 2 or data_figures['-'] != 1 ):
                self.statusBar().showMessage(self.error_incorrect_data)
                self.statusBar().setStyleSheet(self.error_message)
            elif data_current <= datetime.datetime.now():
                self.statusBar().showMessage(self.error_past_date)
                self.statusBar().setStyleSheet(self.error_message)
            else:
                try:
                    id_cinema = \
                    self.cur.execute('SELECT * from Cinema WHERE title = ?', (title_cinema,)).fetchone()[0]
                    hall = self.cur.execute('SELECT * from Halls WHERE number = ? AND cinema = ?', (number_hall, id_cinema)).fetchone()
                    if hall:
                        id_hall = hall[0]
                        length_hall = hall[2]
                        width_hall = hall[1]
                        sessions = self.cur.execute('SELECT data FROM Sessions WHERE cinema_id = ? and hall_id = ?', (id_cinema, id_hall)).fetchall()
                        for i in sessions:
                            first_data = i[0].split('-')[0]
                            second_data = str(i[0].split('-')[0])[:-5] + str(
                                i[0].split('-')[1])
                            data_check = datetime.datetime.strptime(first_data,
                                                                    '%Y.%m.%d %H:%M')
                            data_check_2 = datetime.datetime.strptime(second_data,
                                                                      '%Y.%m.%d %H:%M')
                            if (data_current >= data_check and data_current <= data_check_2) or (data_current_2 >= data_check and data_current_2 <= data_check_2):
                                self.statusBar().showMessage(self.error_data_already)
                                self.statusBar().setStyleSheet(self.error_message)
                                flag_incorect_data = True
                        if not flag_incorect_data:
                            seats = list()
                            for i in range(length_hall):
                                seats.append([])
                                for j in range(width_hall):
                                    seats[-1].append(0)
                            seats = str(seats)
                            self.cur.execute('INSERT INTO Sessions(title, cinema_id, hall_id, data, seats) VALUES (?, ?, ?, ?, ?)', (title, id_cinema, id_hall, data, seats))
                            self.con.commit()
                            self.statusBar().showMessage(self.success_add_session)
                            self.statusBar().setStyleSheet(self.success_message)
                            self.title_cinema_session.setText('')
                            self.number_hall_session.setText('')
                            self.title_session.setText('')
                            self.time_session.setText('')
                    else:
                        self.statusBar().showMessage(self.error_incorrect_data)
                        self.statusBar().setStyleSheet(self.error_message)
                except TypeError:
                    self.statusBar().showMessage(self.error_not_exist_cinema)
                    self.statusBar().setStyleSheet(self.error_message)

    def letters(self, text):
        try:
            text = int(text)
            return False
        except ValueError:
            return True


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design.ui', self)
        self.auth.clicked.connect(self.authtorization)
        self.con = sqlite3.connect('baza.db')
        self.cur = self.con.cursor()
        self.reg.clicked.connect(self.open_registration)
        self.open_authorization()
        self.authorization_btn.clicked.connect(self.open_authorization)
        self.registration_btn.clicked.connect(self.registration)
        self.client_form = Client()
        self.admin_form = Admin()
        self.error_incorrect_data = 'Введены некорректные данные либо же данный пользователь не зарегистрирован'
        self.success_authoriz = 'Вы успешно авторизованы!'
        self.error_user_already_registred = 'Пользователь с данным номером телефона уже зарегистрирован!'
        self.success_registred = 'Вы успешно зарегестрированы!'

    def authtorization(self):
        number_phone = self.input_number.text()
        password = self.input_password.text()
        users = self.cur.execute('SELECT * FROM Users').fetchall()
        for i in users:
            if check_password_hash(i[2], password) and i[4] == int(number_phone):
                self.label_3.setText(self.success_authoriz)
                if i[3]:
                    self.admin_form.show()
                else:
                    self.client_form.data_user(int(number_phone))
                    self.client_form.show()
                self.hide()
        self.label_3.setText(self.error_incorrect_data)

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

    def registration(self):
        number_phone = self.input_number.text()
        password = generate_password_hash(self.input_password.text())
        fio = self.input_fio.text()
        is_admin = 0
        if self.admin.isChecked():
            is_admin = 1
        is_registred_phone = self.cur.execute('SELECT * from Users WHERE number_phone = ?', (int(number_phone),)).fetchone()
        if is_registred_phone:
            self.label_3.setText(self.error_user_already_registred)
        else:
            if password and fio:
                self.cur.execute('INSERT INTO Users (fio, password, is_admin, number_phone) VALUES (?, ?, ?, ?)', (fio, password, is_admin, number_phone))
                self.con.commit()
                self.label_3.setText(self.success_registred)
                if is_admin:
                    self.admin_form.show()
                else:
                    self.client_form.data_user(int(number_phone), fio=fio)
                    self.client_form.show()
                self.hide()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())