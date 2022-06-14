"""
基于pyqt5的界面化操作facebook相关任务的后台处理程序
"""
import json
import os
import sys
import sqlite3
import base64
import random
import time
import requests
import pandas
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
from interface import Ui_Form as MainWindow
from login import Ui_Form as Auth
from configparser import ConfigParser
from Crypto.Cipher import AES

sys.coinit_flags = 2
config = ConfigParser()
config.read('config.ini', encoding='utf-8')
base_url = config['api settings']['base_url']
open_page = config['api settings']['open_page']
close_browser = config['api settings']['close_browser']
sqlite_abs_path = config['sqlite']['abs_path']
open_page_url = f'{base_url}{open_page}'
close_page = f'{base_url}{close_browser}'

connect = sqlite3.connect(sqlite_abs_path)
cursor = connect.cursor()


class TaskModel:
    def __init__(
            self,
            task_type: str,
            _id: 'int|str',
            status: dict,
            pub_page_link: str = None,
            group_link: str = None,
            media_path: str = None,
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


class AuthWindow(QMainWindow, Auth):
    def __init__(self):
        super(AuthWindow, self).__init__()
        self.setupUi(self)
        self.key = b'1590:{^$_-/.2nsb'
        self.iv = b'sheridan214sw78e'
        self.parse_auth_info()

    def parse_auth_info(self):
        sql = 'select Authorization from auth'
        cursor.execute(sql)
        res = cursor.fetchone()
        if res:
            text = self.return_auth(res[0])
            encode_str = base64.encodebytes(text)
            if encode_str.strip().decode('utf-8') in self.__auth_info__():
                self.lineEdit.setText('您已授权！！')
                self.lineEdit.setEnabled(False)
                self.pushButton.setText('点击登录')
                self.pushButton.clicked.connect(self.login)
        else:
            self.pushButton.clicked.connect(self.parse_input_auth)

    def login(self):
        self.close()
        main_window.show()

    def make_password(self, t):
        obj = AES.new(self.key, AES.MODE_CBC, self.iv)
        return obj.encrypt(bytes(t.encode('utf-8')))

    def parse_input_auth(self):
        text = self.lineEdit.text()
        if text:
            encode_str = base64.encodebytes(text.encode('utf-8'))
            info = encode_str.decode('utf-8').strip()
            if info in self.__auth_info__():
                text = self.make_password(text)
                sql = 'insert into auth(Authorization) values (?)'
                cursor.execute(sql, (text, ))
                connect.commit()
                QMessageBox.information(
                    self,
                    '成功！',
                    '您已成功授权！请重新进入本软件!'
                )
                self.close()
                main_window.show()
            else:
                QMessageBox.warning(
                    self,
                    '错误',
                    '授权码错误！'
                )
        else:
            QMessageBox.warning(
                self,
                '错误',
                '请输入授权码！'
            )

    def return_auth(self, s_auth):
        obj = AES.new(self.key, AES.MODE_CBC, self.iv)
        text = obj.decrypt(s_auth)
        return text

    @staticmethod
    def __auth_info__():
        auth_list = [
            'NDU1M2FmNTVjOTM3NGFmOWEzZjdhMGM1ZDJlYTllNTc=',
            'YmEzNmMxMDYzYTg1NDAwNGJjYTY5Mjk3M2Y0YjVmZjc=',
            'Yzk1NGYxYWZiMWY1NDFiMDg5MmRiNDdlOWQwOThmNzQ=',
            'ODhmNjQxM2Q2YTNjNDhmN2IwNWU5NWFmNGI4MjUzMjU='
        ]
        return auth_list


class FaceBookTask(QMainWindow, MainWindow):
    def __init__(self):
        super(FaceBookTask, self).__init__()
        self.setWindowIcon(QIcon('a4ttb-t6tco-002.ico'))
        self.setupUi(self)
        self.show_interface()
        self.set_combobox_text()
        self.choose_account_list = list()  # 多账号任务账号列表

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
        self.pushButton_ok.clicked.connect(self.confirm_account)
        self.pushButton_get_account_list.clicked.connect(self.get_account_list)
        self.pushButton_open_excel.clicked.connect(self.choose_excel)
        self.pushButton_del_task.clicked.connect(self.del_task)
        self.pushButton_refresh.clicked.connect(self.set_combobox_text)
        self.pushButton_add_friends.clicked.connect(lambda: self.parse_task('add_friend'))
        self.pushButton_confirm_friend_request.clicked.connect(lambda: self.parse_task('confirm_friend'))
        self.pushButton_invite_like.clicked.connect(lambda: self.parse_task('invite_like'))
        self.pushButton_share_page.clicked.connect(lambda: self.parse_task('share_page'))
        self.pushButton_add_group.clicked.connect(lambda: self.parse_task('add_group'))
        self.pushButton_like.clicked.connect(lambda: self.parse_task('like'))
        self.pushButton_public_own.clicked.connect(lambda: self.parse_task('publish_own'))
        self.pushButton_public_all.clicked.connect(lambda: self.parse_task('publish_public_page'))

    def confirm_account(self):
        self.set_combobox_text()
        self.choose_account_list = list()
        count = self.listWidget.count()
        checkbox_list = [self.listWidget.itemWidget(self.listWidget.item(i)) for i in range(count)]
        for checkbox in checkbox_list:
            if checkbox.isChecked():
                self.choose_account_list.append(checkbox.text())

        QMessageBox.information(
            self,
            '提示',
            '确认成功'
        )

        # print(self.choose_account_list)

    def get_account_list(self):
        self.listWidget.clear()
        sql = 'select id, profile_id, nickname from task where info = 1'
        cursor.execute(sql)
        result = cursor.fetchall()
        # print(result)
        for r in result:
            task_id, profile_id, nickname = r
            box = QCheckBox(f'{task_id}--{nickname}--{profile_id}')
            item = QListWidgetItem()
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, box)

    def start_task(self, status, id_, profile_id, task_type, like_link, group_link, media_path):
        task_model = TaskModel(
            task_type=task_type,
            status=json.loads(status),
            _id=id_,
            pub_page_link=like_link,
            group_link=group_link,
            media_path=media_path
        )
        backend = StartTask(profile_id=profile_id, task_model=task_model, parent=self)
        backend.update_data.connect(self.handle_task)
        backend.model_data.connect(self.update_status)
        backend.start()

    def parse_task(self, task_type):
        self.disable_button()
        id_ = self.comboBox.currentText().split('--')[0].strip()
        if id_ == '选择一个任务' and self.choose_account_list:
            for data in self.choose_account_list:
                id_, nickname, profile_id = data.split('--')
                sql = 'select status, like_link, group_link, media_path from task where id = ?'
                cursor.execute(sql, (id_,))
                status, like_link, group_link, media_path = cursor.fetchone()
                self.start_task(status, id_, profile_id, task_type, like_link, group_link, media_path)
            self.choose_account_list = list()
        elif id_ == '选择一个任务' and not self.choose_account_list:
            QMessageBox.warning(
                self,
                '注意',
                '批量任务请确认，单个任务请选择!!!'
            )
            self.able_button()
        else:
            sql = 'select profile_id, status, like_link, group_link, media_path from task where id = ?'
            cursor.execute(sql, (id_,))
            try:
                self.disable_button()
                profile_id, status, like_link, group_link, media_path = cursor.fetchone()
                self.start_task(status, id_, profile_id, task_type, like_link, group_link, media_path)
            except TypeError:
                self.able_button()

    def update_status(self, data: TaskModel):
        status = data.status
        id_ = data.id_
        sql = 'update task set `status` = ? where id = ?'
        cursor.execute(sql, (
            json.dumps(status, ensure_ascii=False),
            id_
        ))
        connect.commit()
        self.textEdit.append('完成了一次任务, 已更新status')

    def handle_task(self, data):
        if data == 'start':
            self.disable_button()
        elif data == 'end':
            self.able_button()
        elif data == '权限不足':
            QMessageBox.warning(
                self,
                "权限不足",
                '没有足够的权限\n请关闭本软件并使用管理员权限运行!!'
            )
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
        try:
            df = pandas.read_excel(file)
            data_list = df.values
        except FileNotFoundError:
            data_list = list()
            QMessageBox.warning(
                self,
                '文件选择错误',
                '请正确选择文件'
            )
        try:
            for data in data_list:
                _id, pub, group, media, nickname = data
                status = json.dumps({
                    "添加推荐好友": 0,
                    "确认好友请求": 0,
                    "邀请好友点赞": 0,
                    "分享公共主页": 0,
                    "点赞帖子": 0,
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
    model_data = pyqtSignal(TaskModel)

    def __init__(self, profile_id, task_model: TaskModel, parent=None):
        super(StartTask, self).__init__(parent)
        self.task_model = task_model
        self.profile_id = profile_id
        self.driver = StartChrome(self.profile_id).start_chrome()
        self.task_dict = {
            'add_friend': 'self.add_friend()',
            'confirm_friend': 'self.confirm_friend()',
            'invite_like': 'self.invite_like()',
            'share_page': 'self.share_page()',
            'add_group': 'self.add_group()',
            'like': 'self.like()',
            'publish_own': 'self.publish_own()',
            'publish_public_page': 'self.publish_public_page()'
        }

    def publish_public_page(self):
        self.update_data.emit('开始在公共主页发表文章')
        import pywinauto
        from pywinauto.keyboard import send_keys
        if self.task_model.media_path:
            dir_path = self.task_model.media_path
            try:
                file_list = os.listdir(dir_path)
            except FileNotFoundError:
                self.update_data.emit('文件路径不存在')
                file_list = None

            if file_list:
                # print(file_list)
                picture_list = [f'"{i}"' for i in file_list if 'txt' not in i]
                # print(picture_list)
                text_path = self.task_model.media_path + r'\txt.txt'
                # print(text_path)
                with open(text_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                try:
                    self.driver.get('https://www.facebook.com/pages/?category=your_pages&ref=bookmarks')
                    value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/a'
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
                    WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located((By.XPATH, '//div[@aria-label="发帖"]'))).click()
                    value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div/div/div/div[2]/div'
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).send_keys(
                        content)
                    WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located((By.XPATH, '//div[@aria-label="照片/视频"]'))).click()
                    app = pywinauto.Desktop()
                    window = app['打开']
                    window['Toolbar3'].click()
                    send_keys(self.task_model.media_path)
                    send_keys("{VK_RETURN}")
                    window['文件名(&N):Edit'].type_keys(' '.join(picture_list))
                    time.sleep(1)
                    # window["打开(&O)"].click()
                    send_keys("{VK_RETURN}")
                    time.sleep(10)
                    element = self.driver.find_elements(by=By.XPATH, value='//div[@aria-label="发帖"]')[-1]
                    element.click()
                except RuntimeError:
                    self.update_data.emit('权限不足')
                except Exception as e:
                    self.update_data.emit('发表失败！！')
        else:
            self.update_data.emit('没有找到文件路径')

        self.task_model.status['公共主页发表帖子'] += 1
        self.close_browser()

    def publish_own(self):
        import pywinauto
        from pywinauto.keyboard import send_keys
        self.update_data.emit(f'开始在个人主页发表帖子')
        if self.task_model.media_path:
            dir_path = self.task_model.media_path
            try:
                file_list = os.listdir(dir_path)
            except FileNotFoundError:
                self.update_data.emit('文件路径不存在!!!')
                file_list = None
            if file_list:
                print(file_list)
                picture_list = [f'"{i}"' for i in file_list if 'txt' not in i]
                print(picture_list)
                text_path = self.task_model.media_path + r'\txt.txt'
                print(text_path)
                with open(text_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                print(content)
                try:
                    self.driver.get('https://www.facebook.com')
                    value = '//body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div/div[1]/div'
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
                    value = '//body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[2]/div[1]/div[1]/div[1]/div/div/div/div/div/div/div[2]/div'
                    try:
                        WebDriverWait(self.driver, 5).until(ec.presence_of_element_located((By.XPATH, value))).send_keys(
                            content)
                    except Exception as e:
                        value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[2]/div[1]/div[1]/div[1]/div/div/div[1]'
                        WebDriverWait(self.driver, 5).until(ec.presence_of_element_located((By.XPATH, value))).send_keys(content)
                    value = '//body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[3]/div[1]/div[2]/div/div[1]/div/span/div'
                    WebDriverWait(self.driver, 3).until(ec.presence_of_element_located((By.XPATH, value))).click()
                    value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[1]/div/div/div'
                    WebDriverWait(self.driver, 5).until(ec.presence_of_element_located((By.XPATH, value))).click()
                    app = pywinauto.Desktop()
                    window = app['打开']
                    window['Toolbar3'].click()
                    send_keys(self.task_model.media_path)
                    send_keys("{VK_RETURN}")
                    window['文件名(&N):Edit'].type_keys(' '.join(picture_list))
                    time.sleep(1)
                    # window["打开(&O)"].click()
                    send_keys("{VK_RETURN}")
                    time.sleep(5)
                    value = '//div[@aria-label="发帖"]'

                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
                    time.sleep(10)
                except RuntimeError:
                    self.update_data.emit('权限不足')
                except Exception as e:
                    self.update_data.emit('发表失败！')
        else:
            self.update_data.emit('没有找到这个文件路径耶')

        self.task_model.status['个人主页发表帖子'] += 1
        self.close_browser()

    def like(self):
        self.update_data.emit('开始点赞帖子')
        self.driver.get('https://www.facebook.com')
        for _ in range(10):
            try:
                time.sleep(1)
                self.driver.execute_script(f'window.scrollBy(0, {random.randint(500, 1000)})')
            except Exception as e:
                time.sleep(3)
                continue
        value = '//div[@aria-label="赞"]'
        like_element = self.driver.find_elements(by=By.XPATH, value=value)
        _ = 1
        for element in like_element[::-1]:
            try:
                self.update_data.emit(f'点赞第{_}条帖子')
                time.sleep(1.5)
                element.click()
                self.driver.execute_script(f'window.scrollBy(0, -{random.randint(300, 700)})')
            except selenium.common.exceptions.ElementClickInterceptedException:
                self.update_data.emit(f'第{_}条帖子点赞失败!')
                self.driver.execute_script(f'window.scrollBy(0, -{random.randint(500, 1000)})')
            _ += 1

        self.task_model.status['点赞帖子'] += 1
        self.close_browser()

    def add_group(self):
        self.update_data.emit('开始加入指定小组')
        if self.task_model.group_link:
            self.driver.get(self.task_model.group_link)
            value = '//div[@aria-label="加入小组"]'
            time.sleep(5)
            try:
                element = self.driver.find_elements(by=By.XPATH, value=value)[0]
                element.click()
            except Exception as e:
                self.update_data.emit('加入指定小组失败')
            time.sleep(3)
            self.task_model.status['加入指定公共小组'] += 1
            self.close_browser()
        else:
            self.update_data.emit('没有找到小组链接')
            self.close_browser()

    def share_page(self):
        self.update_data.emit('开始分享指定公共主页')
        if self.task_model.pub_page_link:
            self.driver.get(self.task_model.pub_page_link)
            for _ in range(3):
                time.sleep(1)
                try:
                    self.driver.execute_script(f'window.scrollBy(0, {random.randint(1000, 1500)})')
                except Exception as e:
                    time.sleep(3)
                    continue
            time.sleep(3)
            value = '//div[@role="main"]/div[@class="k4urcfbm"]/div/div/div/div/div[@role="article"]/div/div/div/div/div/div[2]/div/div[last()]/div/div/div/div/div/div/div[last()]/div[@role="button"]'
            share_element = self.driver.find_elements(by=By.XPATH, value=value)
            # print(share_element)
            for element in share_element[:3]:
                try:
                    element.click()
                    share_value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div[1]/div/div[1]/div'
                    WebDriverWait(self.driver, 5).until(ec.presence_of_element_located((By.XPATH, share_value))).click()
                    time.sleep(2)
                except Exception as e:
                    pass
            self.task_model.status['分享公共主页'] += 1
            self.close_browser()
        else:
            self.update_data.emit('没有找到公共主页链接')
            self.close_browser()

    def invite_like(self):
        self.update_data.emit('开始邀请好友为公共主页点赞')
        if self.task_model.pub_page_link:
            self.driver.get(self.task_model.pub_page_link)
            try:
                value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[3]/div/div/div/div[2]/div/div/div[3]/div'
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
                value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[4]'
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            except Exception as e:
                value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div[3]/div/div/div/div[2]/div/div/div[2]/div'
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
                value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div[3]/div[4]'
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            time.sleep(5)
            value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div[5]/div/div[1]/div[@data-visualcompletion="ignore-dynamic"]/div[@role="checkbox"]'
            check_box_element = self.driver.find_elements(by=By.XPATH, value=value)

            for element in check_box_element[:5]:
                time.sleep(1.5)
                element.click()

            value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div[2]/div'
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            time.sleep(3)
            self.task_model.status['邀请好友点赞'] += 1
            self.close_browser()

        else:
            self.update_data.emit('没有找到链接。。。')
            self.close_browser()

    def close_browser(self):
        headers = {'id': self.profile_id}
        requests.post(close_page, json=headers)
        self.model_data.emit(self.task_model)
        self.update_data.emit('refresh')
        self.update_data.emit('end')

    def add_friend(self):
        info = '正在进行确认好友请求任务.....'
        self.update_data.emit(info)
        try:
            self.driver.get('https://www.facebook.com/friends/suggestions')
        except selenium.common.exceptions.WebDriverException:
            self.update_data.emit('网络不通畅')
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
        self.task_model.status['添加推荐好友'] += 1
        self.close_browser()

    def confirm_friend(self):
        self.update_data.emit('正在进行确认好友请求操作...')
        self.driver.get('https://www.facebook.com/friends/requests')
        time.sleep(3)
        value = '//div[@role="navigation"]/div/div[2]/div/div[2]/div/div/div/div/a/div/div[2]/div/div[2]/div/div/div[1]/div[@role="button"]'
        confirm_friends_request_element = self.driver.find_elements(by=By.XPATH, value=value)
        _ = 1
        for element in confirm_friends_request_element[:5]:
            time.sleep(1.5)
            self.update_data.emit(f'完成第{_}个')
            element.click()
            _ += 1
        time.sleep(3)
        self.task_model.status['确认好友请求'] += 1
        self.close_browser()

    def run(self):
        if self.driver == 'error_1':
            self.update_data.emit('browser_error')
        elif self.driver == 'error_2':
            self.update_data.emit('profile_error')
        else:
            eval(self.task_dict.get(self.task_model.task_type))


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_window = FaceBookTask()
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec_())



