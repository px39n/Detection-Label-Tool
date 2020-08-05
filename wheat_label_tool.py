# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pandas as pd
class ImageBox(QWidget):
    def __init__(self):
        super(ImageBox, self).__init__()
        self.img = None         #img
        self.scaled_img = None  #
        self.point = QPoint(0, 0)
        self.start_pos = None
        self.end_pos = None
        self.left_click = False
        self.scale = 1
        self.move=False
        self.setCursor(Qt.PointingHandCursor)

    def set_image(self, img_path):
        """
        open image file
        :param img_path: image file path
        :return:
        """
        global pointlist
        pointlist = []
        self.img = QPixmap(img_path)
        self.w = self.img.width()
        self.h = self.img.height()
        self.setFixedSize(1280,1048)
        print(self.img.width())
        self.scaled_img =self.img

        self.repaint()


    def paintEvent(self, e):
        """
        receive paint events
        :param e: QPaintEvent
        :return:
        """
        if self.scaled_img:
            painter = QPainter()
            painter.begin(self)
            painter.drawPixmap(self.point.x(), self.point.y(), self.w, self.h, self.scaled_img)
            pen=QtGui.QPen(QtCore.Qt.red)
            pen.setWidth(10)
            painter.setPen(pen)

            for p in pointlist:
                x=int(self.point.x()+self.scale*p[0])
                y=int(self.point.y()+self.scale*p[1])

                painter.drawPoint(x,y)

            painter.end()


    def wheelEvent(self, event):

        angle = event.angleDelta() / 8  #
        angleX = angle.x()
        angleY = angle.y()
        if angleY > 0:
            self.w = self.w*(1+0.1)
            self.h = self.h*(1+0.1)
            self.point=self.point+self.point*0.1
            self.scale = self.w / self.img.width()
            self.repaint()

        else:  # 滚轮下滚
            self.w = self.w * (1 - 0.1)
            self.h = self.h * (1 - 0.1)
            self.point = self.point -self.point * 0.1
            self.scale = self.w / self.img.width()
            self.repaint()



    def mouseMoveEvent(self, e):
        """
        mouse move events for the widget
        :param e: QMouseEvent
        :return:
        """
        if self.left_click:
            self.end_pos = e.pos() - self.start_pos
            self.point = self.point + self.end_pos
            self.start_pos = e.pos()
            self.repaint()
            self.move = True

    def mousePressEvent(self, e):
        """
        mouse press events for the widget
        :param e: QMouseEvent
        :return:
        """
        if e.button() == Qt.LeftButton:
            self.left_click = True
            self.start_pos = e.pos()

    def mouseReleaseEvent(self, e):
        """
        mouse release events for the widget
        :param e: QMouseEvent
        :return:
        """
        if e.button() == Qt.LeftButton:
            self.left_click = False
        if not self.move:
            self.scale=self.w/self.img.width()
            a=e.pos()-self.point
            a=a/self.scale
            pointlist.append([a.x(),a.y()])
            b=[str(i) for i in pointlist ]
            slm = QStringListModel()
            slm.setStringList(b)
            win.listView2.setModel(slm)
            self.repaint()
        self.move = False


class ListViewDemo(QMainWindow):
    def __init__(self, parent=None):
        super(ListViewDemo, self).__init__(parent)
        self.imgName = []
        self.resize(400, 350)

        HLayout = QHBoxLayout()
        VLayout1= QVBoxLayout()
        VLayout = QVBoxLayout()

        # bar menu
        bar = self.menuBar()
        file = bar.addMenu("File")
        edit = bar.addMenu("Help")
        edit.addAction("right click POINT to delete")
        edit.addAction("click dir to switch img")

        #image area
        global path
        self.box = ImageBox()
        path='D:\Code\GeneralTool\File\IMG_1.jpg'
        self.box.set_image(path)
        VLayout1.addWidget(self.box)
        # self.lab2 = QLabel("coordinate")
        # VLayout1.addWidget(self.lab2)
        HLayout.addLayout(VLayout1)

        #point_list area
        self.listView2 = QListView()
        self.listView2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView2.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow2)
        global pointlist
        pointlist=[]

        # file area
        self.listView = QListView()
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)
        self.selectbtn = QPushButton("Import Image")
        self.btnOK = QPushButton("Save Label")
        #groupBox = QGroupBox("是否使用GPU")


        #layout
        layout = QHBoxLayout()
        #groupBox.setLayout(layout)
        VLayout.addWidget(self.selectbtn)
        VLayout.addWidget(self.btnOK)
        #VLayout.addWidget(groupBox)
        VLayout.addWidget(self.listView)
        HLayout.addLayout(VLayout)
        HLayout.addWidget(self.listView2)
        main_frame = QWidget()
        main_frame.setLayout(HLayout)

        #connect signal slot
        self.setWindowTitle("Wheat_Label_tool")
        self.selectbtn.clicked.connect(self.openimage)
        self.listView.clicked.connect(self.clicked)
        self.btnOK.clicked.connect(self.savepoint)
        self.setCentralWidget(main_frame)


    def rightMenuShow(self):
        rightMenu = QtWidgets.QMenu(self.listView)
        removeAction = QtWidgets.QAction(u"Delete", self,
                                         triggered=self.removeimage)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def rightMenuShow2(self):
        rightMenu = QtWidgets.QMenu(self.listView)
        removeAction = QtWidgets.QAction(u"Delete", self,
                                         triggered=self.removepoint)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def removepoint(self):
        selected = self.listView2.selectedIndexes()
        itemmodel = self.listView2.model()
        for i in selected:
            itemmodel.removeRow(i.row())
            #print(i.row())
            pointlist.pop(i.row())
        self.repaint()

    def clicked(self, qModelIndex):
        # QMessageBox.information(self, "QListView", "你选择了: "+ imgName[qModelIndex.row()])

        self.box.set_image(QPixmap(imgName[qModelIndex.row()]))
        global path
        path = imgName[qModelIndex.row()]

    def openimage(self):
        global imgName
        imgName, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "File Selection", "/", "All (*)")
        slm = QStringListModel()
        slm.setStringList(imgName)
        self.listView.setModel(slm)

    def removeimage(self):
        selected = self.listView.selectedIndexes()
        itemmodel = self.listView.model()
        for i in selected:
            itemmodel.removeRow(i.row())

    def savepoint(self):
        #print(path)
        (filepath,filename) = os.path.split(path)
        filename=os.path.splitext(filename)[0]+"_GT.csv"
        filepath=filepath+"\label\\"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        pd.DataFrame(pointlist).to_csv(filepath+filename,index=False,header=False,encoding="utf_8_sig")
        QMessageBox.information(self, "Save", "Success")
        slm = QStringListModel()
        slm.setStringList([])
        self.listView2.setModel(slm)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ListViewDemo()
    win.show()
    sys.exit(app.exec_())

