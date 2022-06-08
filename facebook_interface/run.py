import sys
from facebook_interface.facebook_easy_task import FaceBookTask
from PyQt5.QtWidgets import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = FaceBookTask()
    main.show()
    sys.exit(app.exec_())




