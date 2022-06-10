import json
import sys
import pandas
import sqlite3

import requests
import random
from typing import List
import time
import requests
import pandas
import pywinauto
from pywinauto.keyboard import send_keys
import selenium
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
from interface import Ui_Form
from settings import *

connect = sqlite3.connect('facebook_task.db')
cursor = connect.cursor()


class TaskModel:
    def __init__(
            self,
            task_type: str,
            _id: 'int|str' = None,
            pub_page_link: str = None,
            group_link: str = None,
            media_path: str = None,
            status: dict = None,
            nickname: str = None
    ):
        self.id_ = _id
        self.task_type = task_type
        self.pub_page_link = pub_page_link
        self.group_link = group_link
        self.media_path = media_path
        self.status = status
        self.nickname = nickname


class StartChrome:
    def __init__(self, profile_sid):
        self.profile_sid = profile_sid

    def start_chrome(self):
        headers = {'id': self.profile_sid}
        try:
            host_port = requests.post(open_page_url, json=headers).json()
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


class FaceBookTask(QMainWindow, Ui_Form):
    def __init__(self):
        super(FaceBookTask, self).__init__()
        self.setupUi(self)
        self.show_interface()
        self.set_combobox_text()

    def set_combobox_text(self):
        self.label_show_task_status.clear()
        sql = 'select id, profile_id, nickname from task where info = 1'
        cursor.execute(sql)
        res = cursor.fetchall()
        self.comboBox.clear()
        self.comboBox.addItem('选择一个任务')
        for r in res:
            self.comboBox.addItem(f'{r[0]}--{r[-1]}--{r[1]}')

        self.comboBox.currentIndexChanged.connect(self.show_account_info)

    def show_account_info(self):
        profile_id = self.comboBox.currentText().split('--')[-1].strip()
        sql = 'select status from task where profile_id = ? and info = 1'
        cursor.execute(sql, (profile_id,))
        try:
            res = cursor.fetchone()[0]
            data: dict = json.loads(res)
            string = ''
            _ = 1
            for k, v in data.items():
                string += f'{k}--{v}\t\t\t'
                if _ % 2 == 0:
                    string += '\n'
                _ += 1
            string += '\n 注: 数字为完成次数'
            self.label_show_task_status.setText(string)
        except TypeError:
            pass

    def show_interface(self):
        self.pushButton_open_excel.clicked.connect(self.choose_excel)
        self.pushButton_del_task.clicked.connect(self.del_task)
        self.pushButton_refresh.clicked.connect(self.set_combobox_text)
        self.pushButton_add_friends.clicked.connect(self.add_friend)

    def add_friend(self):
        id_ = self.comboBox.currentText().split('--')[0].strip()
        sql = 'select profile_id, status from task where id = ?'
        cursor.execute(sql, (id_,))
        try:
            self.disable_button()
            profile_id, status = cursor.fetchone()
            task_model = TaskModel(task_type='add_friend', status=json.loads(status), _id=id_)
            backend = StartTask(profile_id=profile_id, task_model=task_model, parent=self)
            backend.update_data.connect(self.handle_task)
            backend.dict_data.connect(self.update_status)
            backend.start()
        except TypeError:
            self.able_button()
            pass

    def update_status(self, data):
        id_ = self.comboBox.currentText().split('--')[0].strip()
        sql = 'update task set `status` = ? where id = ?'
        cursor.execute(sql, (
            json.dumps(data, ensure_ascii=False),
            id_
        ))
        connect.commit()

    def handle_task(self, data):
        if data == 'start':
            self.disable_button()
        elif data == 'end':
            self.able_button()
        elif data == 'browser_error':
            QMessageBox.warning(
                self,
                '浏览器唤起错误',
                '请检查settings.py中的浏览器端口是否正确'
            )
            self.able_button()
        elif data == 'profile_error':
            QMessageBox.warning(
                self,
                '浏览器配置文件错误',
                '请检查浏览器配置文件是否正确'
            )
            self.able_button()
        elif data == 'refresh':
            self.set_combobox_text()
        else:
            self.textEdit.append(data)

    def disable_button(self):
        self.comboBox.setEnabled(False)
        self.pushButton_add_friends.setEnabled(False)
        self.pushButton_confirm_friend_request.setEnabled(False)
        self.pushButton_invite_like.setEnabled(False)
        self.pushButton_share_page.setEnabled(False)
        self.pushButton_add_group.setEnabled(False)
        self.pushButton_like.setEnabled(False)
        self.pushButton_public_own.setEnabled(False)
        self.pushButton_public_all.setEnabled(False)
        self.pushButton_public_group.setEnabled(False)

    def able_button(self):
        self.comboBox.setEnabled(True)
        self.pushButton_add_friends.setEnabled(True)
        self.pushButton_confirm_friend_request.setEnabled(True)
        self.pushButton_invite_like.setEnabled(True)
        self.pushButton_share_page.setEnabled(True)
        self.pushButton_add_group.setEnabled(True)
        self.pushButton_like.setEnabled(True)
        self.pushButton_public_own.setEnabled(True)
        self.pushButton_public_all.setEnabled(True)
        self.pushButton_public_group.setEnabled(True)

    def del_task(self):
        _id = self.comboBox.currentText().split('--')[0].strip()
        sql = 'update task set info = 0 where id = ?'
        cursor.execute(sql, (_id,))
        connect.commit()
        self.set_combobox_text()

    def choose_excel(self):
        file, ok = QFileDialog.getOpenFileName(
            self,
            '选择一个Excel',
            'C:/',
            'Excel Files (*.xls *.xlsx)'
        )

        df = pandas.read_excel(file)
        data_list = df.values
        try:
            for data in data_list:
                _id, pub, group, media, nickname = data
                status = json.dumps({
                    "添加推荐好友": 0,
                    "确认好友请求": 0,
                    "邀请好友点赞": 0,
                    "分享公共主页": 0,
                    "加入指定公共小组": 0,
                    "个人主页发表帖子": 0,
                    "公共主页发表帖子": 0,
                    "小组发表帖子": 0
                }, ensure_ascii=False)
                cursor.execute(
                    'insert into task (profile_id, like_link, group_link, media_path, nickname, status) '
                    'values (?, ?, ?, ?, ?, ?)', (_id, pub, group, media, nickname, status)
                )
                connect.commit()
            self.label_show_file_path.setText('已入库--' + file)
            self.set_combobox_text()
        except ValueError:
            QMessageBox.warning(
                self,
                '出错啦!',
                '请按照给定的Excel任务模板进行添加！'
            )
            self.label_show_file_path.setText('入库失败本文件')


class StartTask(QThread):
    update_data = pyqtSignal(str)
    dict_data = pyqtSignal(dict)

    def __init__(self, profile_id, task_model: TaskModel, parent=None):
        super(StartTask, self).__init__(parent)
        self.task_model = task_model
        self.profile_id = profile_id
        self.driver = StartChrome(self.profile_id).start_chrome()

    def confirm_friends_requests(self):
        info = '正在进行确认好友请求任务.....'
        self.update_data.emit(info)
        self.driver.get('https://www.facebook.com/friends/suggestions')
        value = '//div[@role="navigation"]/div/div[2]/div/div[2]/div/div/div/a/div/div[2]/div/div[2]/div/div/div/div[@role="button"]'
        try:
            time.sleep(2)
            self.driver.find_elements(by=By.XPATH, value=value)[0].click()

            value = '//div[@role="navigation"]/div/div[2]/div/div/div/div/div/a/div/div[2]/div/div[2]/div/div[1]/div[1]/div[@role="button"]'
            find_friend_element = self.driver.find_elements(by=By.XPATH, value=value)
            _ = 1
            for element in find_friend_element[1:6]:
                time.sleep(1.5)
                element.click()
                info = f'成功同意--第{_}个'
                self.update_data.emit(info)
                _ += 1
        except Exception as e:
            info += '任务中断。。。'

            pass
        time.sleep(2)
        headers = {'id': self.profile_id}
        requests.post(close_page, json=headers)

    def run(self):
        if self.driver == 'error_1':
            self.update_data.emit('browser_error')
        elif self.driver == 'error_2':
            self.update_data.emit('profile_error')
        else:
            if self.task_model.task_type == 'add_friend':
                self.confirm_friends_requests()
                self.task_model.status['添加推荐好友'] += 1
                self.dict_data.emit(self.task_model.status)
                self.update_data.emit('refresh')
                self.update_data.emit('end')


def run():
    app = QApplication(sys.argv)
    main = FaceBookTask()
    main.show()
    sys.exit(app.exec())
