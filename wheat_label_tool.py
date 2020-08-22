# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pandas as pd
import cv2
class ImageBox(QWidget):
    def __init__(self):
        super(ImageBox, self).__init__()
        self.img = None         #img
        self.path = None
        self.key=127
        self.gray = None   # semi gray img
        self.ref_img=None
        self.scaled_img = None  #
        self.point = QPoint(0, 0)
        self.start_pos = None
        self.end_pos = None
        self.left_click = False
        self.scale = 1
        self.move=False
        self.setCursor(Qt.PointingHandCursor)
        self.start_click=False
        self.line=[0,0]
        self.pos=None
        self.grayview=False


    def set_image(self):
        """
        open image file
        :param img_path: image file path
        :return:
        """
        global pointlist
        pointlist = []

        self.img = QPixmap(self.path)

        self.w = self.img.width()
        self.h = self.img.height()
        self.setFixedSize(1280,1048)

        self.scaled_img =self.img

        key = self.key
        gray = cv2.imread(self.path, 0)
        self.gray = gray
        ret, gray = cv2.threshold(gray, key, 255, cv2.THRESH_BINARY)
        gray = cv2.fastNlMeansDenoising(gray)
        gray = QImage(gray, gray.shape[1], gray.shape[0], QtGui.QImage.Format_Grayscale8)

        self.ref_img= QPixmap(gray)

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
            if self.grayview:
                painter.drawPixmap(self.point.x(), self.point.y(), self.w, self.h, self.ref_img)
            else:
                painter.drawPixmap(self.point.x(), self.point.y(), self.w, self.h, self.scaled_img)
            pen=QtGui.QPen(QtCore.Qt.red)
            pen.setWidth(6)
            painter.setPen(pen)

            for p in pointlist:
                x1=int(self.point.x()+self.scale*p[0])
                y1=int(self.point.y()+self.scale*p[1])
                x2 = int(self.point.x() + self.scale * p[2])
                y2 = int(self.point.y() + self.scale * p[3])
                painter.drawLine(x1,y1,x2,y2)
            if self.start_click:
                x1 = int(self.point.x() + self.scale * self.line[0])
                y1 = int(self.point.y() + self.scale * self.line[1])
                painter.drawLine(x1, y1, self.pos.x(), self.pos.y())



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
        if self.start_click:
            self.pos=e.pos()
            self.repaint()





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
        global pointlist
        if e.button() == Qt.LeftButton:
            self.left_click = False

        if not self.move:
            self.start_click = not self.start_click
            self.scale=self.w/self.img.width()
            a=e.pos()-self.point
            a=a/self.scale
            #pointlist.append([2,5])
            if self.start_click:
                self.line=[a.x(),a.y()]
            else:
                self.line.append(a.x())
                self.line.append(a.y())
                pointlist.append(self.line)
                self.line=None
                b=[str(i) for i in pointlist]
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
        edit.addAction("can use Ctrl+S to save")
        edit.addAction("can use Ctrl+Z to withdraw")
        edit.addAction("can use shift to switch view")
        #image area
        global path
        self.box = ImageBox()
        self.box.path='D:\Code\GeneralTool\File\IMG_1.jpg'
        self.box.set_image()
        self.box.setMouseTracking(True)
        VLayout1.addWidget(self.box)
        # self.lab2 = QLabel("coordinate")
        # VLayout1.addWidget(self.lab2)
        HLayout.addLayout(VLayout1)

        #point_list area
        self.listView2 = QListView()
        self.listView2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView2.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow2)

        # file area
        self.listView = QListView()
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)
        self.selectbtn = QPushButton("Import Image")
        self.btnOK = QPushButton("Save Label")
        self.cb1 = QCheckBox('Switch View')
        self.mySlider = QSlider(Qt.Horizontal, self)
        self.mySlider.setMinimum(20)
        self.mySlider.setMaximum(245)
        self.mySlider.setSingleStep(100)
        self.mySlider.setTickInterval(50)
        self.mySlider.setTickPosition(QSlider.TicksBelow)

        #layout
        layout = QHBoxLayout()
        #groupBox.setLayout(layout)
        VLayout.addWidget(self.selectbtn)
        VLayout.addWidget(self.btnOK)
        VLayout.addWidget(self.cb1)
        VLayout.addWidget(self.mySlider)
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
        self.cb1.stateChanged.connect(self.changecb1)
        self.mySlider.valueChanged[int].connect(self.changeValue)
    def rightMenuShow(self):
        rightMenu = QtWidgets.QMenu(self.listView)
        removeAction = QtWidgets.QAction(u"Delete", self,
                                         triggered=self.removeimage)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def changecb1(self):
        if self.cb1.checkState() == Qt.Checked:
            self.box.grayview=True
        elif self.cb1.checkState() == Qt.Unchecked:
            self.box.grayview=False
        self.mySlider.setValue(self.box.key)
        self.box.repaint()

    def changeValue(self,value):
        key = value
        gray = self.box.gray
        ret, gray = cv2.threshold(gray, key, 255, cv2.THRESH_BINARY)
        gray = cv2.fastNlMeansDenoising(gray)
        gray = QImage(gray, gray.shape[1], gray.shape[0], QtGui.QImage.Format_Grayscale8)
        self.box.ref_img= QPixmap(gray)
        self.box.key=key
        self.box.repaint()

    def rightMenuShow2(self):
        rightMenu = QtWidgets.QMenu(self.listView)
        removeAction = QtWidgets.QAction(u"Delete", self,
                                         triggered=self.removepoint)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def removepoint(self):
        global pointlist
        selected = self.listView2.selectedIndexes()
        itemmodel = self.listView2.model()
        for i in selected:
            itemmodel.removeRow(i.row())
            #print(i.row())
            pointlist.pop(i.row())
        self.repaint()

    def keyPressEvent(self, event):
        global pointlist
        if event.key() == (Qt.Key_Control and Qt.Key_S):
            self.savepoint()
            b = [str(i) for i in pointlist]
            self.set_list(b)
            self.repaint()

        if event.key() == (Qt.Key_Control and Qt.Key_Z):
            pointlist.pop(-1)
            b = [str(i) for i in pointlist]
            self.set_list(b)
            self.repaint()

        if event.key() == (Qt.Key_Shift):
            if not self.cb1.isChecked():
                self.cb1.setChecked(True)
            else:
                self.cb1.setChecked(False)

    def clicked(self, qModelIndex):
        # QMessageBox.information(self, "QListView", "你选择了: "+ imgName[qModelIndex.row()])
        self.box.path=imgName[qModelIndex.row()]

        self.box.set_image()
        global path
        global pointlist
        path = imgName[qModelIndex.row()]
        (label_path, filename) = os.path.split(path)
        filename = label_path+"/label/"+os.path.splitext(filename)[0] + "_GT.csv"
        pointlist=[]
        b=pointlist
        if os.path.exists(filename):
            file=pd.read_csv(filename,
                             ",", header=None).values
            pointlist = file.tolist()
            b=[str(i) for i in pointlist]
        self.set_list(b)
        self.repaint()


    def openimage(self):
        global imgName
        imgName, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "File Selection", "D:/Data/wheat ears counting", "All (*)")
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
        self.set_list([])

    def set_list(self,pts_list):
        slm = QStringListModel()
        slm.setStringList(pts_list)
        self.listView2.setModel(slm)

if __name__ == "__main__":
    pointlist = []
    app = QApplication(sys.argv)
    win = ListViewDemo()
    win.show()
    sys.exit(app.exec_())

