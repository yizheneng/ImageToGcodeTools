#coding=utf-8
from PyQt4.QtGui import QMainWindow, QLabel, QSpinBox, QPushButton, QPixmap,\
    qGray
from PyQt4.Qt import QWidget, QVBoxLayout, QDoubleSpinBox, QHBoxLayout, QFileDialog, QMessageBox,\
    QImage, qRgb, QVector2D

class MainWindow(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(500, 300)
        
        self.mainLayout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.pixLayout = QHBoxLayout()
        self.thresholdLayout = QHBoxLayout()
        self.timeLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Image To Gcode ----- build By yizheneng kangbo0303@163.com")
        
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
        
        self.loadImageButton = QPushButton(u"加载图片")
        self.loadImageButton.clicked.connect(self.LoadImageButtonClicked)
        self.previewButton = QPushButton(u"预览")
        self.previewButton.clicked.connect(self.ThresholdValChange)
        self.makeCodeButton = QPushButton(u"生成G代码")
        self.makeCodeButton.clicked.connect(self.MakeGcode)
        
        
        self.layout.addLayout(self.pixLayout)
        self.layout.addLayout(self.thresholdLayout)
        self.layout.addLayout(self.timeLayout)
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
        self.imageLabel.setPixmap(QPixmap(self.srcImage))
        
    def ThresholdValChange(self):
        for i in range(self.srcImage.width()):
            for j in range(self.srcImage.height()):
                temp = self.srcImage.pixelIndex(i, j)
                if(temp >= self.thresholdSpinBox.value()):
                    self.grayImage.setPixel(i, j, 255)
                else:
                    self.grayImage.setPixel(i, j, 0)
        
        self.imageLabel.setPixmap(QPixmap(self.grayImage))
        
    def MakeGcode(self):
        path = QFileDialog.getSaveFileName(self, u"选择保存路径", "", " (*.nc)")
        if path == "":
            QMessageBox.warning(self, u"发生错误", u"路径错误！！")
            return 
        
        f = open(path, 'w')
        f.write("M5\n")
        
        for i in range(self.grayImage.width()):
            flag = False
            #检测这一行是否有点
            for j in range(self.grayImage.height()):
                if self.srcImage.pixelIndex(i, j) < 128:
                    flag = True
                    break
            #如果这一行都没有点则跳过这一行
            if flag:
                f.write("G0 Y%f\n"% (i * self.pixDoubleSpinBox.value()))
            else:
                continue
            
            if (i % 2) > 0:
                for j in range(self.grayImage.height()):
                    if self.srcImage.pixelIndex(i, j) < 128:
                        f.write("G0 X%f\n" % (j * self.pixDoubleSpinBox.value()))
                        f.write("M3\n")
                        f.write("G4 P%f\n" % self.timeDoubleSpinBox.value())
                        f.write("M5\n")
            else:
                for j in range(self.grayImage.height())[::-1]:
                    if self.srcImage.pixelIndex(i, j) < 128:
                        f.write("G0 X%f\n" % (j * self.pixDoubleSpinBox.value()))
                        f.write("M3\n")
                        f.write("G4 P%f\n" % self.timeDoubleSpinBox.value())
                        f.write("M5\n")
                    
        f.write("M5\n")
        f.write("G0 X0 Y0\n")
        f.close()
        QMessageBox.information(self, u"成功", u"生成G代码文件成功！！")