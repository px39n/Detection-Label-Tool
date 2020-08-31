import pandas as pd
import cv2
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import qimage2ndarray as q2n
from utils import binarization


class ImageBox(QWidget):
    def __init__(self):
        super(ImageBox, self).__init__()

        #the label list
        self.line_list = []

        # the size,path start point of show area
        self.path = None  # original img_path
        self.scale = 1
        self.w=None
        self.h=None
        self.point = QPoint(0, 0)

        # the original,gray, and scaled images
        self.img = None
        self.gray_threshold=127
        self.np_gray = None       # numpy format
        self.qpixel_gray=None     # Qpixel format


        #flags
        self.start_pos = None
        self.end_pos = None
        self.is_left_clicked = False
        self.is_moving=False
        self.setCursor(Qt.PointingHandCursor)
        self.is_drawing=False
        self.line=[]
        self.pos=None
        self.is_grayview=False


    def set_image(self):
        """
        open image file
        :param img_path: image file path
        :return:
        """
        #initialize the img, size,
        self.setFixedSize(1280, 1048)
        self.img = QPixmap(self.path)
        self.w = self.img.width()
        self.h = self.img.height()

        #set and save the gray image
        self.np_gray=cv2.imread(self.path,0)
        modified_gray = q2n.array2qimage(binarization(self.np_gray,self.gray_threshold))
        self.qpixel_gray= QPixmap(modified_gray)

        self.repaint()


    def paintEvent(self, e):
        """
        receive paint events
        :param e: QPaintEvent
        :return:
        """

        #draw the img
        if self.img:
            painter = QPainter()
            painter.begin(self)
            if self.is_grayview:
                painter.drawPixmap(self.point.x(), self.point.y(), self.w, self.h, self.qpixel_gray)
            else:
                painter.drawPixmap(self.point.x(), self.point.y(), self.w, self.h, self.img)

            # set the size and color of pen
            pen=QtGui.QPen(QtCore.Qt.red)
            pen.setWidth(6)
            painter.setPen(pen)

            #draw the finished line
            for p in self.line_list:
                x1=int(self.point.x()+self.scale*p[0])
                y1=int(self.point.y()+self.scale*p[1])
                x2 = int(self.point.x() + self.scale * p[2])
                y2 = int(self.point.y() + self.scale * p[3])
                painter.drawLine(x1,y1,x2,y2)

            #draw the unfinished line
            if self.is_drawing:
                x1 = int(self.point.x() + self.scale * self.line[0])
                y1 = int(self.point.y() + self.scale * self.line[1])
                painter.drawLine(x1, y1, self.pos.x(), self.pos.y())

            painter.end()

        b = [str(i) for i in self.line_list]
        slm = QStringListModel()
        slm.setStringList(b)
        self.bigbox.listView2.setModel(slm)

    def wheelEvent(self, event):

        #scale the image
        angle = event.angleDelta() / 8
        angleX = angle.x()
        angleY = angle.y()
        if angleY > 0:
            self.w = self.w*(1+0.1)
            self.h = self.h*(1+0.1)
            self.point=self.point+self.point*0.1
            self.scale = self.w / self.img.width()
            self.repaint()

        else:
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

        #
        if self.is_left_clicked:
            self.end_pos = e.pos() - self.start_pos
            self.point = self.point + self.end_pos
            self.start_pos = e.pos()
            self.repaint()
            self.is_moving = True

        #record the position of mouse to draw the line while drawing
        if self.is_drawing:
            self.pos=e.pos()
            self.repaint()

    def mousePressEvent(self, e):

        #change flag
        if e.button() == Qt.LeftButton:
            self.is_left_clicked = True
            self.start_pos = e.pos()

    def mouseReleaseEvent(self, e):

        #change flag
        if e.button() == Qt.LeftButton:
            self.is_left_clicked = False
            #record the line or point
            if not self.is_moving:

                #calculate the absolute position
                self.scale=self.w/self.img.width()
                absolute_position=e.pos()-self.point
                a=absolute_position/self.scale

                #start recording or finish recording
                if self.is_drawing:
                    self.update_line(a)
                else:
                    self.update_line(a)
                self.is_drawing = not self.is_drawing
            self.is_moving = False

    def update_line(self,abs):
        self.line.append(abs.x())
        self.line.append(abs.y())
        if len(self.line) >3:
            print("WTFFFFF")
            self.line_list.append(self.line)
            self.repaint()
            self.line = []

class object_detection(QMainWindow):
    def __init__(self, parent=None):
        super(object_detection, self).__init__(parent)
        self.imgName = []
        self.resize(400, 350)

        # bar menu
        importAct = QAction('Import', self, triggered=self.openimage)
        saveAct = QAction('Save', self, triggered=self.savepoint)
        saveAct.setShortcut('Ctrl+S')
        undoAct= QAction('Undo', self, triggered=self.undo)
        undoAct.setShortcut('Ctrl+Z')
        exitAct = QAction('Exit', self, triggered=self.close)

        exitAct.setShortcut('Ctrl+Q')
        bar = self.menuBar()
        file = bar.addMenu("File")
        edit = bar.addMenu("Help")
        file.addActions((importAct,saveAct,undoAct,exitAct))
        edit.addAction("right click POINT to delete")
        edit.addAction("click dir to switch img")

        # imagebox
        self.box = ImageBox()
        self.box.path='./Sample/Sample_A.jpg'
        self.box.set_image()
        self.box.setMouseTracking(True)
        self.box.bigbox=self

        # pointlist
        self.listView2 = QListView()
        self.listView2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView2.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow2)
        # FileList
        self.listView = QListView()
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)
        # Button
        self.import_btn = QPushButton("Import Image")
        self.save_btn = QPushButton("Save Label")
        self.switch_cb = QCheckBox('Switch View (Shift)')
        self.mySlider = QSlider(Qt.Horizontal, self)
        self.mySlider.setMinimum(20)
        self.mySlider.setMaximum(245)
        self.mySlider.setValue(125)
        self.mySlider.setTickPosition(QSlider.TicksBelow)

        # connect signal slot
        self.setWindowTitle("Wheat_Label_tool")
        self.import_btn.clicked.connect(self.openimage)
        self.listView.clicked.connect(self.lv_loadimg)
        self.save_btn.clicked.connect(self.savepoint)
        self.switch_cb.stateChanged.connect(self.change_switch_cb)
        self.mySlider.valueChanged[int].connect(self.changeValue)


        #layout
        HLayout = QHBoxLayout()
        VLayout1= QVBoxLayout()
        VLayout = QVBoxLayout()
        VLayout1.addWidget(self.box)
        HLayout.addLayout(VLayout1)
        VLayout.addWidget(self.import_btn)
        VLayout.addWidget(self.save_btn)
        VLayout.addWidget(self.switch_cb)
        VLayout.addWidget(self.mySlider)
        VLayout.addWidget(self.listView)
        HLayout.addLayout(VLayout)
        HLayout.addWidget(self.listView2)
        main_frame = QWidget()
        main_frame.setLayout(HLayout)
        self.setCentralWidget(main_frame)

    def rightMenuShow(self):
        rightMenu = QtWidgets.QMenu(self.listView)
        removeAction = QtWidgets.QAction(u"Delete", self,
                                         triggered=self.removeimage)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def change_switch_cb(self):
        if self.switch_cb.checkState() == Qt.Checked:
            self.box.is_grayview=True
        elif self.switch_cb.checkState() == Qt.Unchecked:
            self.box.is_grayview=False
        self.box.repaint()

    def changeValue(self,value):
        self.box.gray_threshold = value
        modified_gray = q2n.array2qimage(binarization(self.box.np_gray,self.box.gray_threshold))
        self.box.qpixel_gray= QPixmap(modified_gray)
        self.box.repaint()

    def rightMenuShow2(self):
        rightMenu = QtWidgets.QMenu(self.listView2)
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
            self.box.line_list.pop(i.row())
        self.repaint()

    def keyPressEvent(self, event):
        if event.key() == (Qt.Key_Shift):
            if not self.switch_cb.isChecked():
                self.switch_cb.setChecked(True)
            else:
                self.switch_cb.setChecked(False)

    def undo(self):
        self.box.line_list.pop(-1)
        self.repaint()

    def lv_loadimg(self, qModelIndex):

        self.box.path=imgName[qModelIndex.row()]
        self.box.set_image()
        self.box.path = imgName[qModelIndex.row()]
        (label_path, filename) = os.path.split(self.box.path)
        filename = label_path+"/label/"+os.path.splitext(filename)[0] + "_GT.csv"
        self.box.line_list=[]
        b=self.box.line_list
        if os.path.exists(filename):
            file=pd.read_csv(filename,
                             ",", header=None).values
            self.box.line_list = file.tolist()
            b=[str(i) for i in self.box.line_list]
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

        (filepath,filename) = os.path.split(self.box.path)
        filename=os.path.splitext(filename)[0]+"_GT.csv"
        filepath=filepath+"\label\\"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        pd.DataFrame(self.box.line_list).to_csv(filepath+filename,index=False,header=False,encoding="utf_8_sig")
        QMessageBox.information(self, "Save", "Success")
        self.set_list([])

    def set_list(self,pts_list):
        slm = QStringListModel()
        slm.setStringList(pts_list)
        self.listView2.setModel(slm)
