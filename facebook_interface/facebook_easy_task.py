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
from tqdm import tqdm
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
from facebook_interface.interface import Ui_Form
from facebook_interface.settings import *


class TaskModel:
    def __init__(
            self,
            browser_id,
            pub_page_link,
            group_link,
            media_path
    ):
        self.id = browser_id
        self.pub_page_link = pub_page_link
        self.group_link = group_link
        self.media_path = media_path


class StartChrome:
    def __init__(self, profile_sid):
        self.profile_sid = profile_sid

    def start_chrome(self):
        headers = {'id': self.profile_sid}
        host_port = requests.post(open_page_url, json=headers).json()
        host_port = host_port.get('data').get('http')
        chrome_driver = Service("chromedriver.exe")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", host_port)
        driver = webdriver.Chrome(service=chrome_driver, options=chrome_options)

        return driver


class FaceBookTask(QMainWindow, Ui_Form):
    def __init__(self):
        super(FaceBookTask, self).__init__()
        self.setupUi(self)
        self.show_interface()
        self.set_combobox_text()

    def set_combobox_text(self):
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
                    'values (?, ?, ?, ?, ?, ?)',  (_id, pub, group, media, nickname, status)
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

    def __init__(self, profile_id, task_model, parent=None):
        super(StartTask, self).__init__(parent)
        self.task_model = task_model
        self.profile_id = profile_id
        self.driver = StartChrome(self.profile_id).start_chrome()

    def confirm_friends_requests(self):
        info = '正在进行确认好友请求任务.....\n'
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
                info += f'成功同意--第{_}个\n'
                self.update_data.emit(info)
        except Exception as e:
            info += '任务中断。。。\n'

            pass
        time.sleep(2)
        headers = {'id': self.task_model.id}
        requests.post(close_page, json=headers)


if __name__ == '__main__':
    connect = sqlite3.connect('facebook_task.db')
    cursor = connect.cursor()
    app = QApplication(sys.argv)
    main = FaceBookTask()
    main.show()
    sys.exit(app.exec_())
