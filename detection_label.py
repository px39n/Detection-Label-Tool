# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from object_detection import *
from change_detection import *


class choose(QMainWindow):
    def __init__(self, parent=None):
        super(choose, self).__init__(parent)

        self.resize(400, 350)
        self.change_btn = QPushButton("Change Detection")
        self.object_btn = QPushButton("Object Detection")

        self.setWindowTitle("Label_Detection")
        self.change_btn.clicked.connect(self.change_btnf)
        self.object_btn.clicked.connect(self.object_btnf)

        VLayout = QVBoxLayout()
        VLayout.addWidget(self.change_btn)
        VLayout.addWidget(self.object_btn)

        main_frame = QWidget()
        main_frame.setLayout(VLayout)
        self.setCentralWidget(main_frame)
    def change_btnf(self):
        win_1=change_detection()
        win_1.show()
        self.close()

    def object_btnf(self):
        win_2=object_detection()
        win_2.show()
        self.close()


if __name__ == "__main__":
    pointlist = []
    app = QApplication(sys.argv)
    win = choose()
    win.show()
    sys.exit(app.exec_())

