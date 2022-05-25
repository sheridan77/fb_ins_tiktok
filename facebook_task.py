# -*- coding: utf-8 -*-
"""
基于比特浏览器的Facebook自动化脚本
@File    :    facebook_task.py
@Author  :    Sheridan 77
@Time    :    2022/5/20
@Version :    V 1.0.0
@Desc    :    fb自动化脚本
@contact :    zrq17777813307@163.com
"""
import sys
import os
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

from settings import *


# 开启浏览器并用selenium接手
class StartChrome:
    def __init__(self, profile_sid):
        self.profile_sid = profile_sid

    def start_chrome(self):
        headers = {'id': self.profile_sid}
        host_port = requests.post(open_page_url, json=headers).json()
        host_port = host_port.get('data').get('http')
        chrome_driver = "chromedriver.exe"
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", host_port)
        driver = webdriver.Chrome(chrome_driver, options=chrome_options)

        return driver


# 存储任务信息的模板
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


# 执行facebook自动化任务
class FacebookTask:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.task = self.get_task()
        # print(self.task[0].group_link)
        self.start_task()

    def get_task(self) -> List[TaskModel]:
        """
        获取任务
        :return: 任务模型列表
        """
        df = pandas.read_excel(self.excel_path)
        data_list = df.values
        task_list = list()
        for data in data_list:
            _id, pub, group, media = data
            task_model = TaskModel(
                browser_id=_id,
                pub_page_link=pub,
                group_link=group,
                media_path=media
            )
            task_list.append(task_model)
        return task_list

    def start_task(self):
        """开始任务"""
        task_num = 0
        for i in tqdm(range(1, len(self.task) + 1)):

            one_task = self.task[task_num]
            # 每一个任务对应一个浏览器配置
            driver = StartChrome(one_task.id).start_chrome()
            current_windows = driver.window_handles
            driver.switch_to.window(current_windows[-1])
            # 添加推荐好友
            # driver.get('https://www.facebook.com/friends/suggestions')
            # value = '//div[@role="navigation"]/div/div[2]/div/div[2]/div/div/div/a/div/div[2]/div/div[2]/div/div/div/div[@role="button"]'
            # try:
            #     driver.find_elements(by=By.XPATH, value=value)[0].click()
            #
            #     value = '//div[@role="navigation"]/div/div[2]/div/div/div/div/div/a/div/div[2]/div/div[2]/div/div[1]/div[1]/div[@role="button"]'
            #     find_friend_element = driver.find_elements(by=By.XPATH, value=value)
            #     for element in find_friend_element[1:6]:
            #         time.sleep(1.5)
            #         element.click()
            # except Exception as e:
            #     pass
            # time.sleep(2)
            # # 同意好友请求 5个
            # driver.get('https://www.facebook.com/friends/requests')
            # value = '//div[@role="navigation"]/div/div[2]/div/div[2]/div/div/div/div/a/div/div[2]/div/div[2]/div/div/div[1]/div[@role="button"]'
            # confirm_friends_request_element = driver.find_elements(by=By.XPATH, value=value)
            # for element in confirm_friends_request_element[:5]:
            #     time.sleep(1.5)
            #     element.click()
            # time.sleep(3)
            # # 邀请好友为指定的公共主页点赞 5位好友
            # if str(one_task.pub_page_link) != 'nan':
            #     driver.get(one_task.pub_page_link)
            #     try:
            #         value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[3]/div/div/div/div[2]/div/div/div[3]/div'
            #         WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #         value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[4]'
            #         WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #     except Exception as e:
            #         value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div[3]/div/div/div/div[2]/div/div/div[2]/div'
            #         WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #         value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div[3]/div[4]'
            #         WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #     time.sleep(5)
            #     value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div[5]/div/div[1]/div[@data-visualcompletion="ignore-dynamic"]/div[@role="checkbox"]'
            #     check_box_element = driver.find_elements(by=By.XPATH, value=value)
            #     for element in check_box_element[:5]:
            #         time.sleep(1.5)
            #         element.click()
            #
            #     value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div[2]/div'
            #     WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #     time.sleep(3)
            # # 指定公共主页分享
            #     driver.get(one_task.pub_page_link)
            #     for _ in range(3):
            #         time.sleep(1)
            #         driver.execute_script(f'window.scrollBy(0, {random.randint(200, 500)})')
            #     time.sleep(3)
            #     value = '//div[@role="main"]/div[@class="k4urcfbm"]/div/div/div/div/div[@role="article"]/div/div/div/div/div/div[2]/div/div[last()]/div/div/div/div/div/div/div[last()]/div[@role="button"]'
            #     share_element = driver.find_elements(by=By.XPATH, value=value)
            #     # print(share_element)
            #     for element in share_element[:3]:
            #         try:
            #             element.click()
            #             share_value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div[1]/div/div[1]/div'
            #             WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, share_value))).click()
            #             time.sleep(2)
            #         except Exception as e:
            #             pass
            # if str(one_task.group_link) != 'nan':
            #     # 加入指定公共小组
            #     driver.get(one_task.group_link)
            #     value = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div[1]/div[1]/div[2]/div/div[4]/div/div/div/div/div[1]/div'
            #     WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #     try:
            #         value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div[2]/div'
            #         WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #         value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div[4]/div/div/div/div[2]/div[1]'
            #         WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, value))).click()
            #     except Exception as e:
            #         pass
            #     time.sleep(3)
            # 发表帖子
            if str(one_task.media_path) != 'nan':
                dir_path = one_task.media_path
                file_list = os.listdir(dir_path)
                # print(file_list)
                picture_list = [f'"{i}"' for i in file_list if 'txt' not in i]
                # print(picture_list)
                text_path = one_task.media_path + r'\txt.txt'
                # print(text_path)
                with open(text_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                # print(content)

                driver.get('https://www.facebook.com')
                value = '//body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div/div[1]/div'
                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
                value = '//body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[2]/div[1]/div[1]/div[1]/div/div/div/div/div/div/div[2]/div'
                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).send_keys(content)
                value = '//body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[3]/div[1]/div[2]/div/div[1]/div/span/div'
                WebDriverWait(driver, 3).until(ec.presence_of_element_located((By.XPATH, value))).click()
                value = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[1]/div/div/div'
                WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, value))).click()
                app = pywinauto.Desktop()
                window = app['打开']
                window['Toolbar3'].click()
                send_keys(one_task.media_path)
                send_keys("{VK_RETURN}")
                window['文件名(&N):Edit'].type_keys(' '.join(picture_list))
                time.sleep(1)
                # window["打开(&O)"].click()
                send_keys("{VK_RETURN}")
                time.sleep(5)
                value = '//div[@aria-label="发帖"]'

                WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, value))).click()
                time.sleep(10)
            # 点赞帖子
            # driver.get('https://www.facebook.com')
            # for _ in range(10):
            #     time.sleep(1)
            #     driver.execute_script(f'window.scrollBy(0, {random.randint(500, 1000)})')
            # time.sleep(3)
            # value = '//div[@role="feed"]/div/div/div/div/div/div/div/div/div/div/div/div[last()]/div/div[last()]/div/div/div[1]/div/div[last()]/div/div[1]/div[@aria-label="赞"]'
            # like_element = driver.find_elements(by=By.XPATH, value=value)
            # for element in like_element[::-1]:
            #     time.sleep(1.5)
            #     element.click()
            # headers = {'id': one_task.id}  # TODO 比特浏览器
            # requests.post(close_page, json=headers)
            # task_num += 1
            # print(f'正在进行第{task_num}个任务中，共计{len(self.task)}个任务')
            # # time.sleep(1)
            # os.system('cls')


if __name__ == '__main__':
    fb = FacebookTask(facebook_xlsx_path)
