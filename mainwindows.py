#coding=utf-8
from PyQt4.QtGui import QMainWindow, QSpinBox, QPushButton, QPixmap,\
    qGray, QCheckBox
    
from PyQt4.Qt import QWidget, QVBoxLayout, QDoubleSpinBox, QHBoxLayout, QFileDialog, QMessageBox,\
    QImage, qRgb, QLabel
    
import cv2 as cv
import numpy as np

class MainWindow(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(500, 300)
        
        self.mainLayout = QHBoxLayout()
        self.chooseLayout = QHBoxLayout()
        self.continuousLayout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.pixLayout = QHBoxLayout()
        self.thresholdLayout = QHBoxLayout()
        self.timeLayout = QHBoxLayout()
        self.contoursLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Image To Gcode V1.0 ----- build By yizheneng kangbo0303@163.com")
        
        self.imageLabel = QLabel("image")
        
        self.mainLayout.addWidget(self.imageLabel)
        self.mainLayout.addLayout(self.layout)
        self.mainLayout.setStretchFactor(self.layout, 1)
        self.mainLayout.setStretchFactor(self.imageLabel, 3)
        
        self.pixLengthLabel = QLabel(u"像素大小(mm):")
        self.pixDoubleSpinBox = QDoubleSpinBox()
        self.pixDoubleSpinBox.setValue(1)
        self.pixDoubleSpinBox.setDecimals(6)
        self.pixLayout.addWidget(self.pixLengthLabel)
        self.pixLayout.addWidget(self.pixDoubleSpinBox)
        
        self.thresholdLabel = QLabel(u"阈值:")
        self.thresholdSpinBox = QSpinBox()
        self.thresholdSpinBox.valueChanged.connect(self.ThresholdValChange)
        self.thresholdSpinBox.setMaximum(255)
        self.thresholdSpinBox.setValue(120)
        self.thresholdLayout.addWidget(self.thresholdLabel)
        self.thresholdLayout.addWidget(self.thresholdSpinBox)
        
        self.timeLabel = QLabel(u"灼烧时间:")
        self.timeDoubleSpinBox = QDoubleSpinBox()
        self.timeDoubleSpinBox.setValue(0.3)
        self.timeLayout.addWidget(self.timeLabel)
        self.timeLayout.addWidget(self.timeDoubleSpinBox)
        
        self.chooseLabel = QLabel(u"只雕刻轮廓:")
        self.chooseBox = QCheckBox()
        self.chooseLayout.addWidget(self.chooseLabel)
        self.chooseLayout.addWidget(self.chooseBox)
        self.chooseBox.stateChanged.connect(self.ChooseValChanged)
        
        self.continuousLabel = QLabel(u"连续雕刻:")
        self.continuousBox = QCheckBox()
        self.continuousBox.setEnabled(False)
        self.continuousBox.stateChanged.connect(self.ChooseValChanged)
        self.continuousLayout.addWidget(self.continuousLabel)
        self.continuousLayout.addWidget(self.continuousBox)
        
        self.contoursWidthLabel = QLabel(u"边框宽度")
        self.ContoursWidthSpinBox = QSpinBox()
        self.ContoursWidthSpinBox.setEnabled(False)
        self.ContoursWidthSpinBox.setValue(1)
        self.contoursLayout.addWidget(self.contoursWidthLabel)
        self.contoursLayout.addWidget(self.ContoursWidthSpinBox)
        
        
        self.loadImageButton = QPushButton(u"加载图片")
        self.loadImageButton.clicked.connect(self.LoadImageButtonClicked)
        self.previewButton = QPushButton(u"预览")
        self.previewButton.clicked.connect(self.ThresholdValChange)
        self.makeCodeButton = QPushButton(u"生成G代码")
        self.makeCodeButton.clicked.connect(self.MakeGcode)
        
        
        self.layout.addLayout(self.pixLayout)
        self.layout.addLayout(self.thresholdLayout)
        self.layout.addLayout(self.timeLayout)
        self.layout.addLayout(self.chooseLayout)
        self.layout.addLayout(self.continuousLayout)
        self.layout.addLayout(self.contoursLayout)
        self.layout.addWidget(self.loadImageButton)
        self.layout.addWidget(self.previewButton)
        self.layout.addWidget(self.makeCodeButton)
        
    def LoadImageButtonClicked(self):
        self.filePath = QFileDialog.getOpenFileName(self, u"选择图片文件", "", "Images (*.bmp)")
        if self.filePath == "":
            QMessageBox.warning(self, u"发生错误", u"没有选择可以识别的文件！！")
            return
            
        self.srcImage = QImage(self.filePath)
        self.grayImage = QImage(self.srcImage.size(), QImage.Format_Indexed8)
        
        for i in range(256):
            self.grayImage.setColor(i, qRgb(i, i, i))
        
        for i in range(self.srcImage.width()):
            for j in range(self.srcImage.height()):
                temp = qGray(self.srcImage.pixel(i, j))
                self.grayImage.setPixel(i, j, temp)
        
        self.srcImage = QImage(self.grayImage)
        self.resultImage = QImage(self.grayImage)
        self.imageLabel.setPixmap(QPixmap(self.srcImage))
    
    def ChooseValChanged(self):
        self.continuousBox.setEnabled(self.chooseBox.isChecked())
        self.ContoursWidthSpinBox.setEnabled((self.chooseBox.isChecked()) and (not self.continuousBox.isChecked()))
    
    def ThresholdValChange(self):
        for i in range(self.srcImage.width()):
            for j in range(self.srcImage.height()):
                temp = self.srcImage.pixelIndex(i, j)
                if(temp >= self.thresholdSpinBox.value()):
                    self.grayImage.setPixel(i, j, 255)
                else:
                    self.grayImage.setPixel(i, j, 0)
        self.resultImage = QImage(self.grayImage)
        #如果选中了只雕刻轮廓            
        if self.chooseBox.isChecked():
            img = np.zeros((self.grayImage.height(), self.grayImage.width(), 1), np.uint8)
            for i in range(self.grayImage.width()):
                for j in range(self.grayImage.height()):
                    img[j, i] = self.grayImage.pixelIndex(i, j)
            #提取轮廓        
            contours = cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
            img = np.zeros((self.grayImage.height(), self.grayImage.width(), 1), np.uint8)
            cv.drawContours(img, contours[1][:-1], -1, (255, 255, 255), self.ContoursWidthSpinBox.value())
            self.contours = contours[1][:-1]
            #转换轮廓到显示界面
            for i in range(self.resultImage.width()):
                for j in range(self.resultImage.height()):
                    if img[j, i] == 0:
                        self.resultImage.setPixel(i, j, 255)
                    else:
                        self.resultImage.setPixel(i, j, 0)
            
        self.imageLabel.setPixmap(QPixmap(self.resultImage))
        
    def MakeGcode(self):
        path = QFileDialog.getSaveFileName(self, u"选择保存路径", "", " (*.nc)")
        if path == "":
            QMessageBox.warning(self, u"发生错误", u"路径错误！！")
            return 
        
        f = open(path, 'w')
        f.write("M5\n")
        
        if self.continuousBox.isChecked() and self.chooseBox.isChecked():
            for contour in self.contours:
                f.write("G0 X%f Y%f\n" % ((contour[0][0][0] * self.pixDoubleSpinBox.value()), (contour[0][0][1] * self.pixDoubleSpinBox.value())))
                f.write("M3\n")
                for con in contour:
                    f.write("G0 X%f Y%f\n" % ((con[0][0] * self.pixDoubleSpinBox.value()), (con[0][1] * self.pixDoubleSpinBox.value())))
                    
                f.write("G0 X%f Y%f\n" % ((contour[0][0][0] * self.pixDoubleSpinBox.value()), (contour[0][0][1] * self.pixDoubleSpinBox.value())))
                f.write("M5\n")
        else:
            for i in range(self.resultImage.width()):
                flag = False
                #检测这一行是否有点
                for j in range(self.resultImage.height()):
                    if self.resultImage.pixelIndex(i, j) < 128:
                        flag = True
                        break
                #如果这一行都没有点则跳过这一行
                if flag:
                    f.write("G0 Y%f\n"% (i * self.pixDoubleSpinBox.value()))
                else:
                    continue
                
                if (i % 2) > 0:
                    for j in range(self.resultImage.height()):
                        if self.resultImage.pixelIndex(i, j) < 128:
                            f.write("G0 X%f\n" % (j * self.pixDoubleSpinBox.value()))
                            f.write("M3\n")
                            f.write("G4 P%f\n" % self.timeDoubleSpinBox.value())
                            f.write("M5\n")
                else:
                    for j in range(self.resultImage.height())[::-1]:
                        if self.resultImage.pixelIndex(i, j) < 128:
                            f.write("G0 X%f\n" % (j * self.pixDoubleSpinBox.value()))
                            f.write("M3\n")
                            f.write("G4 P%f\n" % self.timeDoubleSpinBox.value())
                            f.write("M5\n")
                    
        f.write("M5\n")
        f.write("G0 X0 Y0\n")
        f.close()
        QMessageBox.information(self, u"成功", u"生成G代码文件成功！！")