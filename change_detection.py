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

        # the label list
        self.poly_list = []

        # the size,path start point of show area
        self.path = None  # original img_path
        self.scale = 1
        self.w = None
        self.h = None
        self.point = QPoint(0, 0)

        # the original,b, and scaled images
        self.img = None

        self.imgB = None  # Qpixel format

        # flags
        self.start_pos = None
        self.end_pos = None
        self.is_left_clicked = False
        self.is_moving = False
        self.setCursor(Qt.PointingHandCursor)
        self.is_drawing = False
        self.line = []
        self.pos = None
        self.is_tempB = False
        self.is_closed=False

    def set_image(self):
        """

        """
        # initialize the img, size,
        self.setFixedSize(1280, 1048)
        self.img = QPixmap(self.path)
        self.w = self.img.width()
        self.h = self.img.height()
        self.point = QPoint(0, 0)
        self.repaint()

    def paintEvent(self, e):
        """
        receive paint events
        :param e: QPaintEvent
        :return:
        """

        # draw the img
        if self.img:
            painter = QPainter()
            painter.begin(self)
            if self.is_tempB:
                painter.drawPixmap(self.point.x(), self.point.y(), self.w, self.h, self.imgB)
            else:
                painter.drawPixmap(self.point.x(), self.point.y(), self.w, self.h, self.img)

            # set the size and color of pen
            pen = QtGui.QPen(QtCore.Qt.red)
            pen.setWidth(6)
            painter.setPen(pen)
            brush = QBrush(QtCore.Qt.red,Qt.FDiagPattern)
            painter.setBrush(brush)
            #draw the finished line
            for p in self.poly_list:
                poly = QPolygon()
                num = int(len(p) / 2)
                for i in range(num):
                    x,y=self.get_absolute_coor([[p[i*2],p[i*2+1]]])
                    poly.append(QPoint(x,y))
                painter.drawPolygon(poly)

            # draw the unfinished line
            if self.is_drawing:
                aaa = self.pos.x()
                bbb = self.pos.y()
                # draw the annotation point
                if self.is_closed:
                    aaa, bbb = self.get_absolute_coor([[self.line[0], self.line[1]]])
                    painter.drawEllipse(QPoint(aaa, bbb), 15, 15)


                #draw the existed line
                num=int(len(self.line)/2)
                if num>1:
                    for i in range(num-1):
                        x1,y1,x2,y2=self.get_absolute_coor([[self.line[2*i],self.line[2*i+1]],
                                                            [self.line[2*(i+1)],self.line[2*(1+i)+1]]])
                        painter.drawLine(x1, y1, x2, y2)
                #draw the last line
                x1,y1= self.get_absolute_coor([[self.line[-2],self.line[-1]]])
                painter.drawLine(x1, y1, aaa, bbb)

            painter.end()
        self.bigbox.set_list()
    def get_absolute_coor(self,coord_list):
        abs_list=[]
        for coor in coord_list:
            x1 = int(self.point.x() + self.scale * coor[0])
            y1 = int(self.point.y() + self.scale * coor[1])
            abs_list.append(x1)
            abs_list.append(y1)
        return abs_list

    def wheelEvent(self, event):

        # scale the image
        angle = event.angleDelta() / 8
        angleX = angle.x()
        angleY = angle.y()
        if angleY > 0:
            self.w = self.w * (1 + 0.1)
            self.h = self.h * (1 + 0.1)
            self.point = self.point + self.point * 0.1
            self.scale = self.w / self.img.width()
            self.repaint()

        else:
            self.w = self.w * (1 - 0.1)
            self.h = self.h * (1 - 0.1)
            self.point = self.point - self.point * 0.1
            self.scale = self.w / self.img.width()
            self.repaint()

    def mouseMoveEvent(self, e):
        """
        mouse move events for the widget
        :param e: QMouseEvent
        :return:
        """
        #move the img
        if self.is_left_clicked:
            self.end_pos = e.pos() - self.start_pos
            self.point = self.point + self.end_pos
            self.start_pos = e.pos()
            self.repaint()
            self.is_moving = True

        # record the position of mouse to draw the line while drawing
        if self.is_drawing:
            self.pos = e.pos()
            x1=int(self.point.x() + self.scale * self.line[0])
            y1=int(self.point.y() + self.scale * self.line[1])
            if abs(self.pos.x()-x1)<15 and abs(self.pos.y()-y1)<15 and len(self.line)>4:
                self.is_closed=True
            else:
                self.is_closed=False
            self.repaint()

    def mousePressEvent(self, e):

        # change flag
        if e.button() == Qt.LeftButton:
            self.is_left_clicked = True
            self.start_pos = e.pos()

    def mouseReleaseEvent(self, e):

        # change flag
        if e.button() == Qt.LeftButton:
            self.is_left_clicked = False
            # record the line or point
            if not self.is_moving:

                # calculate the absolute position
                self.scale = self.w / self.img.width()
                absolute_position = e.pos() - self.point
                a = absolute_position / self.scale

                # start recording or finish recording
                self.is_drawing = True
                if self.is_drawing:
                    self.update_line(a)
                #self.is_drawing = not self.is_drawing
            self.is_moving = False
        if e.button() == Qt.RightButton and not self.is_moving and self.is_drawing:
            rightMenu = QtWidgets.QMenu(self)
            finish_act = QtWidgets.QAction(u"Finish", self,
                                             triggered=lambda: self.update_line(abs,"finish"))
            cancel_act = QtWidgets.QAction(u"Cancel", self,
                                           triggered=lambda: self.update_line(None, "cancel"))
            undo_act = QtWidgets.QAction(u"Undo Ctrl+Z", self,
                                           triggered=self.bigbox.undo)
            rightMenu.addAction(finish_act)
            rightMenu.addAction(undo_act)
            rightMenu.addAction(cancel_act)
            rightMenu.exec_(QtGui.QCursor.pos())

    def update_line(self, abs,flag="draw"):
        if flag=="cancel":
            self.line=[]
            self.is_drawing = False
            self.repaint()
            self.is_closed=False
        else:
            if flag == "finish":
                if len(self.line) > 4:
                    self.is_drawing = False
                    self.is_closed=False
                    self.poly_list.append(self.line)
                    self.repaint()
                    self.line = []

                else:
                    #only two points in list
                    self.update_line(None,"cancel")

            else:
                if self.is_closed:
                    self.update_line(None,"finish")
                else:
                #update points
                    self.line.append(abs.x())
                    self.line.append(abs.y())



class change_detection(QMainWindow):
    def __init__(self, parent=None):
        super(change_detection, self).__init__(parent)
        self.temp_listA=["./Sample/Sample_A.JPG"]
        self.temp_listB = ["./Sample/Sample_B.JPG"]
        self.resize(400, 350)

        # bar menu
        importAct = QAction('Import', self, triggered=self.openimage)

        saveAct = QAction('Save', self, triggered=self.savepoint)
        saveAct.setShortcut('Ctrl+S')
        undoAct = QAction('Undo', self, triggered=self.undo)
        undoAct.setShortcut('Ctrl+Z')
        exitAct = QAction('Exit', self, triggered=self.close)

        exitAct.setShortcut('Ctrl+Q')
        bar = self.menuBar()
        file = bar.addMenu("File")
        edit = bar.addMenu("Help")
        file.addActions((importAct, saveAct, undoAct, exitAct))
        edit.addAction("right click to save polygon")
        edit.addAction("click dir to switch img")

        # imagebox
        self.box = ImageBox()
        self.box.path = './Sample/Sample_A.jpg'
        self.box.set_image()
        self.box.setMouseTracking(True)
        self.box.bigbox = self

        # pointlist
        self.LV_label = QListView()
        self.LV_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.LV_label.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow2)
        # FileList
        self.LV_A = QListView()
        self.LV_B = QListView()

        # Button
        self.import_btn = QPushButton("Import...")
        self.import_btnB = QPushButton("Import...")
        self.label_a=QLabel("Base Image")
        self.label_b = QLabel("Temporary B")
        self.save_btn = QPushButton("Save Label")
        self.switch_cb = QCheckBox('Switch View (Shift)')

        # connect signal slot
        self.setWindowTitle("Change_deteciton_Tool")
        self.import_btn.clicked.connect(lambda : self.openimage("A"))
        self.import_btnB.clicked.connect(lambda: self.openimage("B"))
        self.LV_A.clicked.connect(self.lv_loadimg)
        self.LV_B.clicked.connect(self.lv_loadimgB)
        self.save_btn.clicked.connect(self.savepoint)
        self.switch_cb.stateChanged.connect(self.change_switch_cb)


        # layout
        H_Overall = QHBoxLayout()
        V_Tool = QVBoxLayout()
        V_Imagebox = QVBoxLayout()
        H_TempBox=QHBoxLayout()
        # overall
        H_Overall.addLayout(V_Imagebox)
        H_Overall.addLayout(V_Tool)
        H_Overall.addWidget(self.LV_label)
        # tool Area

        V_Tool.addWidget(self.save_btn)
        V_Tool.addWidget(self.switch_cb)
        V_Tool.addLayout(H_TempBox)

        V_Imagebox.addWidget(self.box)

        TempA=QVBoxLayout()
        TempA.addWidget(self.import_btn)
        TempA.addWidget(self.label_a)
        TempA.addWidget(self.LV_A)
        TempB=QVBoxLayout()
        TempB.addWidget(self.import_btnB)
        TempB.addWidget(self.label_b)
        TempB.addWidget(self.LV_B)
        H_TempBox.addLayout(TempA)
        H_TempBox.addLayout(TempB)

        main_frame = QWidget()
        main_frame.setLayout(H_Overall)
        self.setCentralWidget(main_frame)
        self.set_list()

    def change_switch_cb(self):
        if self.switch_cb.checkState() == Qt.Checked:
            if self.box.imgB:
                self.box.is_tempB = True
                self.box.repaint()
            else:
                QMessageBox.information(self, "Warning", "Please Import Temporary B")
                self.switch_cb.setChecked(False)

        elif self.switch_cb.checkState() == Qt.Unchecked:
            self.box.is_tempB = False
            self.box.repaint()

    def rightMenuShow2(self):
        rightMenu = QtWidgets.QMenu(self.LV_label)
        removeAction = QtWidgets.QAction(u"Delete", self,
                                         triggered=self.removepoint)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def removepoint(self):
        selected = self.LV_label.selectedIndexes()
        itemmodel = self.LV_label.model()
        for i in selected:
            itemmodel.removeRow(i.row())
            # print(i.row())
            self.box.poly_list.pop(i.row())
        self.repaint()

    def keyPressEvent(self, event):
        if event.key() == (Qt.Key_Shift):
            if not self.switch_cb.isChecked():
                self.switch_cb.setChecked(True)
            else:
                self.switch_cb.setChecked(False)

    def undo(self):
        if self.box.is_drawing:
            if len(self.box.line)>2:
                self.box.line.pop(-1)
                self.box.line.pop(-1)
        elif self.box.poly_list:
            self.box.poly_list.pop(-1)
        self.repaint()

    def lv_loadimg(self, qModelIndex):

        self.box.path = self.temp_listA[qModelIndex.row()]
        self.box.set_image()
        (label_path, filename) = os.path.split(self.box.path)
        filename = label_path + "/label/" + os.path.splitext(filename)[0] + "_GT.csv"
        self.box.poly_list = []
        if os.path.exists(filename):
            file = pd.read_csv(filename,
                               ",", header=None).values
            self.box.poly_list = file.tolist()
            self.box.poly_list=[ [a_ for a_ in i if a_ == a_] for i in self.box.poly_list]
            self.set_list(2)
        self.switch_cb.setChecked(False)

    def lv_loadimgB(self, qModelIndex):
        ref = self.temp_listB[qModelIndex.row()]
        if self.temp_listA==[]:
            QMessageBox.information(self, "Warning","Please Import Temporary A Firstly")
        else:
            self.box.imgB=QPixmap(ref)
            self.switch_cb.setChecked(True)
            self.box.repaint()



    def openimage(self,flag):

        imgName, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "File Selection", "D:/Data/wheat ears counting",
                                                                  "All (*)")
        if flag == "A":
            self.temp_listA = imgName
            self.set_list()

        else:
            self.temp_listB = imgName
            self.set_list()


    def savepoint(self):

        (filepath, filename) = os.path.split(self.box.path)
        filename = os.path.splitext(filename)[0] + "_GT.csv"
        filepath = filepath + "\label\\"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        pd.DataFrame(self.box.poly_list).to_csv(filepath + filename, index=False, header=False, encoding="utf_8_sig")
        QMessageBox.information(self, "Save", "Success")
        self.set_list()

    def set_list(self,flag=0):
        if flag==0:
            b=[str(i) for i in self.box.poly_list]
            self.LV_A.setModel(QStringListModel(self.temp_listA))
            self.LV_B.setModel(QStringListModel(self.temp_listB))
            self.LV_label.setModel(QStringListModel(b))
        else:
            self.LV_B.setModel(QStringListModel(self.temp_listB))
