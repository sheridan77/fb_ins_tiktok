import sys
import ctypes
import sqlite3
import time
from configparser import ConfigParser

import pandas
import json
import os
import logging
from logging import handlers

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets, QtCore
from ins_interface import Ui_Form as MainWindow
from settings import Ui_Form as SettingsWindow
from welcome import Ui_Form as WelcomeWindow

logger_name = "ins_task"
logger_level = logging.DEBUG
# 生成logger
logger = logging.getLogger(logger_name)
# 配置logger
logger.setLevel(logger_level)
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
try:
    hf = handlers.TimedRotatingFileHandler(
        "log/" + logger_name + '.log', when='midnight', backupCount=10, encoding='utf-8')
except FileNotFoundError:
    os.mkdir('log')
    hf = handlers.TimedRotatingFileHandler(
        "log/" + logger_name + '.log', when='midnight', backupCount=10, encoding='utf-8')
hf.suffix = '_%Y-%m-%d.log'
hf.setFormatter(formatter)
logger.addHandler(hf)
logging.getLogger('function').addHandler(hf)


class TaskModel:
    def __init__(
            self,
            profile_id: str,
            task_id: 'str|int',
            status: dict,
            open_page_url: str,
            close_page_url:str,
            task_type: str,
            media_path: str = None,
            nickname: str = None
    ):
        self.task_id = task_id
        self.profile_id = profile_id
        self.status = status
        self.task_type = task_type
        self.open_page_url = open_page_url
        self.close_page_url = close_page_url
        self.media_path = media_path
        self.nickname = nickname


class StartChrome:
    def __init__(self, profile_sid, open_page_url):
        self.profile_sid = profile_sid
        self.open_page_url = open_page_url

    def start_chrome(self):
        headers = {'id': self.profile_sid}
        try:
            host_port = requests.post(self.open_page_url, json=headers).json()
            host_port = host_port.get('data').get('http')
            chrome_driver = Service("chromedriver.exe")
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", host_port)
            driver = webdriver.Chrome(service=chrome_driver, options=chrome_options)
            current_windows = driver.window_handles
            driver.switch_to.window(current_windows[-1])

            return driver
        except requests.exceptions.ConnectionError:
            return 'error_1'
        except AttributeError:
            return 'error_2'


class InsTask(MainWindow, QMainWindow):
    def __init__(self):
        super(InsTask, self).__init__()
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.base_url = self.config['api settings']['base_url']
        self.open_page = self.config['api settings']['open_page']
        self.close_browser = self.config['api settings']['close_browser']
        self.sqlite_abs_path = self.config['sqlite']['ins_abs_path']
        self.open_page_url = f'{self.base_url}{self.open_page}'
        self.close_page_url = f'{self.base_url}{self.close_browser}'
        if os.path.exists(self.sqlite_abs_path):
            self.connect = sqlite3.connect(self.sqlite_abs_path)
            self.cursor = self.connect.cursor()
        else:
            self.cursor = None

        self.setupUi(self)
        self.show_interface()
        self.choose_account_list = list()

    def show_interface(self):
        self.pushButton_open_excel.clicked.connect(self.choose_excel)
        self.pushButton_get_account_list.clicked.connect(self.get_account_list)
        self.pushButton_confirm_task.clicked.connect(self.confirm_account)
        self.pushButton_settings.clicked.connect(self.settings)
        self.pushButton_start_task.clicked.connect(self.start_task)
        self.pushButton_del_task.clicked.connect(self.del_task)

    def del_task(self):
        self.choose_account_list = list()
        count = self.listWidget.count()
        checkbox_list = [self.listWidget.itemWidget(self.listWidget.item(i)) for i in range(count)]
        for checkbox in checkbox_list:
            if checkbox.isChecked():
                self.choose_account_list.append(checkbox.text())

        print(self.choose_account_list)
        sql = 'update ins_task set info = 0 where id = ?'
        for account in self.choose_account_list:
            task_id, nickname, profile_id = account.split('--')
            self.cursor.execute(sql, (task_id, ))
            self.connect.commit()

        self.get_account_list()

    def start_task(self):
        if not self.choose_account_list:
            QMessageBox.warning(
                self,
                '警告',
                '未确认任务或任务列表为空！'
            )
            return
        for task in self.choose_account_list:
            task_id, nickname, profile_id = task.split('--')
            if self.radioButton_pub.isChecked():
                task_type = 'pub_article'
            elif self.radioButton_focus.isChecked():
                task_type = 'focus'
            elif self.radioButton_like.isChecked():
                task_type = 'like'
            else:
                return
            sql = 'select status, media_path from ins_task where id = ?'
            self.cursor.execute(sql, (task_id,))
            status, media_path = self.cursor.fetchone()
            task_model = TaskModel(
                task_id=task_id,
                task_type=task_type,
                profile_id=profile_id,
                nickname=nickname,
                status=json.loads(status),
                media_path=media_path,
                open_page_url=self.open_page_url,
                close_page_url=self.close_page_url
            )
            backend = StartTask(profile_id=profile_id, task_model=task_model, parent=self)
            backend.update_data.connect(self.handle_task)
            backend.model_data.connect(self.update_status)
            backend.start()
        self.choose_account_list = list()

    def handle_task(self, data):
        if data == 'profile_error':
            QMessageBox.warning(
                self,
                '浏览器配置文件错误',
                '请检查浏览器配置文件是否正确'
            )
        else:
            self.textEdit.append(data)

    def update_status(self, data: TaskModel):
        sql = 'update ins_task set `status` = ? where id = ?'
        self.cursor.execute(
            sql,
            (
                json.dumps(data.status, ensure_ascii=False),
                data.task_id
            )
        )
        self.connect.commit()
        self.textEdit.append(json.dumps(data.status, ensure_ascii=False))

    def settings(self):
        settings_window.show()
        settings_window.settings_signal.connect(self.refresh_settings)

    def refresh_settings(self):
        self.config.read('config.ini')
        self.base_url = self.config['api settings']['base_url']
        self.open_page = self.config['api settings']['open_page']
        self.close_browser = self.config['api settings']['close_browser']
        self.sqlite_abs_path = self.config['sqlite']['ins_abs_path']
        self.open_page_url = f'{self.base_url}{self.open_page}'
        self.close_page = f'{self.base_url}{self.close_browser}'
        if os.path.exists(self.sqlite_abs_path):
            self.connect = sqlite3.connect(self.sqlite_abs_path)
            self.cursor = self.connect.cursor()
        else:
            QMessageBox.warning(
                self,
                'warning',
                '数据库信息不存在！'
            )

    def confirm_account(self):
        self.choose_account_list = list()
        count = self.listWidget.count()
        checkbox_list = [self.listWidget.itemWidget(self.listWidget.item(i)) for i in range(count)]
        for checkbox in checkbox_list:
            if checkbox.isChecked():
                self.choose_account_list.append(checkbox.text())

        QMessageBox.information(
            self,
            '提示',
            '确认成功！'
        )

    def get_account_list(self):
        self.listWidget.clear()
        sql = 'select id, profile_id, nickname from ins_task where info = 1'
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            for r in result:
                task_id, profile_id, nickname = r
                box = QCheckBox(f'{task_id}--{nickname}--{profile_id}')
                item = QListWidgetItem()
                self.listWidget.addItem(item)
                self.listWidget.setItemWidget(item, box)
        except (sqlite3.OperationalError, AttributeError):
            QMessageBox.warning(
                self,
                '错误',
                '请正确设置sqlite路径！'
            )

    def choose_excel(self):
        file, ok = QFileDialog.getOpenFileName(
            self,
            '选择一个Excel',
            'C:/',
            'Excel File (*.xls *.xlsx)'
        )
        print(file)
        try:
            df = pandas.read_excel(file)
            data_list = df.values
        except FileNotFoundError:
            data_list = list()
            QMessageBox.warning(
                self,
                '文件选择错误',
                '请选择正确的文件'
            )
        try:
            for data in data_list:
                profile_id, nickname, media = data
                status = json.dumps(
                    {
                        "发布帖子": 0,
                        "关注好友": 0,
                        "点赞帖子": 0
                    },
                    ensure_ascii=False
                )
                try:
                    self.cursor.execute(
                        'insert into ins_task (profile_id, nickname, media_path, status, info) '
                        'values (?, ?, ?, ?, ?)',
                        (profile_id, nickname, media, status, 1)
                    )
                    self.connect.commit()
                except AttributeError:
                    QMessageBox.warning(
                        self,
                        '错误',
                        '请正确设置sqlite路径！'
                    )
                    break
                self.label_show_excel_path.setText('已入库--' + file)
        except ValueError:
            QMessageBox.warning(
                self,
                '出错啦',
                '请按照指定的Excel模板进行添加'
            )
            self.label_show_excel_path.setText('入库失败！')


class Settings(SettingsWindow, QMainWindow):
    settings_signal = pyqtSignal(str)

    def __init__(self):
        super(Settings, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.emit_info)

    def emit_info(self):
        config = ConfigParser()
        config.read('config.ini')

        browser_settings = self.lineEdit_port.text()
        sqlite_settings = self.lineEdit.text()
        if browser_settings.strip():
            config.set('api settings', 'base_url', browser_settings.strip())
            config.write(open('config.ini', 'w'))
        if sqlite_settings.strip():
            config.set('sqlite', 'ins_abs_path', sqlite_settings.strip())
            config.write(open('config.ini', 'w'))

        self.settings_signal.emit('ok')
        QMessageBox.information(
            self,
            '成功！',
            '成功更新配置！'
        )
        self.close()

    def closeEvent(self, event):
        confirm = QMessageBox.warning(
            self,
            '确认？',
            '未保存的配置将丢失',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.No:
            event.ignore()
        else:
            self.close()


class StartTask(QThread):
    update_data = pyqtSignal(str)
    model_data = pyqtSignal(TaskModel)

    def __init__(self, profile_id, task_model: TaskModel, parent=None):
        super(StartTask, self).__init__(parent)
        self.task_model = task_model
        self.profile_id = profile_id
        self.driver = StartChrome(self.profile_id, self.task_model.open_page_url).start_chrome()
        self.task_dict = {
            'pub_article': 'self.pub_article()',
            'focus': 'self.focus()',
            'like': 'self.like()'
        }

    def like(self):
        self.update_data.emit(f'{self.task_model.nickname}正在进行点赞任务!')
        logger.info(f'{self.task_model.nickname}正在进行点赞任务!')
        self.driver.get('https://www.instagram.com/')
        time.sleep(3)
        elements = self.driver.find_elements(by=By.XPATH, value='//span[@class="_aamw"]/button')
        _ = 1
        for element in elements[:3]:
            self.update_data.emit(f'正在点赞第{_}个帖子')
            element.click()
            time.sleep(1)
        self.task_model.status['点赞帖子'] += 1
        self.update_data.emit(f'{self.task_model.nickname}点赞完成！')
        logger.info(json.dumps(self.task_model.status, ensure_ascii=False))
        self.close_browser()

    def focus(self):
        self.update_data.emit(f'{self.task_model.nickname}正在关注好友')
        logger.info(f'{self.task_model.nickname}正在关注好友')
        self.driver.get('https://www.instagram.com/explore/people/')
        time.sleep(3)
        elements = self.driver.find_elements(by=By.XPATH, value='//button[@class="_acan _acap _acas"]')
        _ = 1
        for element in elements[:3]:
            self.update_data.emit(f'正在关注第{_}个好友')
            element.click()
            time.sleep(1)
            _ += 1
        self.update_data.emit(f'{self.task_model.nickname}任务完成')
        self.task_model.status['关注好友'] += 1
        logger.info(json.dumps(self.task_model.status, ensure_ascii=False))
        self.close_browser()

    def pub_article(self):
        import pywinauto
        from pywinauto.keyboard import send_keys

        self.update_data.emit(f'{self.task_model.nickname}正在发帖')
        logger.info(f'{self.task_model.nickname}正在发帖')
        self.driver.get('https://www.instagram.com')
        value = '/html/body/div[1]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/nav/div[2]/div/div/div[3]/div/div[3]/div/button'
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
        value = '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button'
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()

        file_list = os.listdir(self.task_model.media_path)
        picture_list = [f'"{i}"' for i in file_list if '.jpg' in i.lower()]
        if len(picture_list) == 1:
            picture_list = [picture_list[0].replace('"', '')]
        # print(picture_list)
        try:
            text_path = self.task_model.media_path + r'\txt.txt'
            # print(text_path)
            with open(text_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            content = None
        app_ = pywinauto.Desktop()
        window = app_['打开']
        window['Toolbar3'].click()
        send_keys(self.task_model.media_path)
        send_keys("{VK_RETURN}")
        picture = '  '.join(picture_list)
        window['文件名(&N):Edit'].type_keys(picture)
        time.sleep(1)
        # window["打开(&O)"].click()
        send_keys("{VK_RETURN}")

        value = '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/div/div[1]/div/div/div[3]/div/button'
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
        time.sleep(1.5)
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
        value = '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/textarea'
        if content:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).send_keys(content)
        time.sleep(1)
        value = '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/div/div[1]/div/div/div[3]/div/button'
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
        time.sleep(20)
        self.update_data.emit(f'{self.task_model.nickname}发帖完成!')
        logger.info(f'{self.task_model.nickname}发帖完成!')
        self.task_model.status['发布帖子'] += 1
        logger.info(json.dumps(self.task_model.status, ensure_ascii=False))
        self.close_browser()

    def close_browser(self):
        headers = {'id': self.profile_id}
        requests.post(self.task_model.close_page_url, json=headers)

    def run(self):
        if self.driver == 'error_1':
            self.update_data.emit('browser_error')
        elif self.driver == 'error_2':
            self.update_data.emit('profile_error')
        else:
            eval(self.task_dict.get(self.task_model.task_type))


class Welcome(QMainWindow, WelcomeWindow):
    def __init__(self):
        super(Welcome, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.show_)

    def is_admin(self):
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            QMessageBox.warning(
                self,
                '错误',
                '请使用管理员权限运行程序！',
                QMessageBox.No | QMessageBox.Ok,
            )
            return False

    def show_(self):
        if self.is_admin():
            main_window.show()
            self.close()
        else:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings_window = Settings()
    main_window = InsTask()
    welcome_window = Welcome()
    welcome_window.show()
    sys.exit(app.exec_())
