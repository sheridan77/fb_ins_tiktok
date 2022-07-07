# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ins_interface.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(670, 481)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 10, 641, 461))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.pushButton_open_excel = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_open_excel.setObjectName("pushButton_open_excel")
        self.gridLayout.addWidget(self.pushButton_open_excel, 0, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.label_show_excel_path = QtWidgets.QLabel(self.layoutWidget)
        self.label_show_excel_path.setText("")
        self.label_show_excel_path.setObjectName("label_show_excel_path")
        self.horizontalLayout.addWidget(self.label_show_excel_path)
        self.pushButton_settings = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_settings.setObjectName("pushButton_settings")
        self.horizontalLayout.addWidget(self.pushButton_settings)
        self.gridLayout_10.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 1, 1, 1)
        self.pushButton_get_account_list = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_get_account_list.setObjectName("pushButton_get_account_list")
        self.gridLayout_4.addWidget(self.pushButton_get_account_list, 0, 0, 1, 1)
        self.pushButton_confirm_task = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_confirm_task.setObjectName("pushButton_confirm_task")
        self.gridLayout_4.addWidget(self.pushButton_confirm_task, 0, 4, 1, 1)
        self.pushButton_del_task = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_del_task.setObjectName("pushButton_del_task")
        self.gridLayout_4.addWidget(self.pushButton_del_task, 0, 2, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_4, 0, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self.layoutWidget)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout_5.addWidget(self.listWidget, 1, 0, 1, 1)
        self.gridLayout_10.addLayout(self.gridLayout_5, 1, 0, 1, 1)
        self.gridLayout_9 = QtWidgets.QGridLayout()
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem2, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_6.addWidget(self.label_2, 0, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem3, 0, 2, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_6, 0, 0, 1, 1)
        self.textEdit = QtWidgets.QTextEdit(self.layoutWidget)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_7.addWidget(self.textEdit, 1, 0, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_7, 0, 0, 1, 1)
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem4, 0, 0, 1, 1)
        self.pushButton_output_log = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_output_log.setObjectName("pushButton_output_log")
        self.gridLayout_8.addWidget(self.pushButton_output_log, 0, 1, 1, 1)
        self.pushButton_output_history_log = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_output_history_log.setObjectName("pushButton_output_history_log")
        self.gridLayout_8.addWidget(self.pushButton_output_history_log, 0, 2, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_8, 1, 0, 1, 1)
        self.gridLayout_10.addLayout(self.gridLayout_9, 1, 1, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.radioButton_pub = QtWidgets.QRadioButton(self.layoutWidget)
        self.radioButton_pub.setObjectName("radioButton_pub")
        self.gridLayout_2.addWidget(self.radioButton_pub, 0, 0, 1, 1)
        self.radioButton_focus = QtWidgets.QRadioButton(self.layoutWidget)
        self.radioButton_focus.setObjectName("radioButton_focus")
        self.gridLayout_2.addWidget(self.radioButton_focus, 0, 1, 1, 1)
        self.radioButton_like = QtWidgets.QRadioButton(self.layoutWidget)
        self.radioButton_like.setObjectName("radioButton_like")
        self.gridLayout_2.addWidget(self.radioButton_like, 0, 2, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.pushButton_start_task = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_start_task.setObjectName("pushButton_start_task")
        self.gridLayout_3.addWidget(self.pushButton_start_task, 0, 1, 1, 1)
        self.gridLayout_10.addLayout(self.gridLayout_3, 2, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "ins任务"))
        self.label.setText(_translate("Form", "选择Excel"))
        self.pushButton_open_excel.setText(_translate("Form", "打开"))
        self.pushButton_settings.setText(_translate("Form", "设置"))
        self.pushButton_get_account_list.setText(_translate("Form", "获取账号列表"))
        self.pushButton_confirm_task.setText(_translate("Form", "确认任务"))
        self.pushButton_del_task.setText(_translate("Form", "删除任务"))
        self.label_2.setText(_translate("Form", "操作日志"))
        self.pushButton_output_log.setText(_translate("Form", "导出日志"))
        self.pushButton_output_history_log.setText(_translate("Form", "导出历史日志"))
        self.radioButton_pub.setText(_translate("Form", "发布帖子"))
        self.radioButton_focus.setText(_translate("Form", "关注"))
        self.radioButton_like.setText(_translate("Form", "点赞帖子"))
        self.pushButton_start_task.setText(_translate("Form", "开始任务"))
