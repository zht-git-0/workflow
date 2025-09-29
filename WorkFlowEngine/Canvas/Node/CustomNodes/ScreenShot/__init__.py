from ..InfoTemplate import InfoTemplate
import cv2
import mss
import numpy as np
from .....Packages import *

class Info(InfoTemplate):
    def __init__(self):
        super().__init__("ScreenShot","屏幕截图")
        self.input=[["logic",False]]
        self.output=[["logic",False],["img",True]]
    def run(self,arg):
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # 获取主显示器
            self.img = sct.grab(monitor)    # 捕获整个屏幕
            self.img = np.array(self.img)        # 将截图转换为numpy数组
            #cv2.imshow("1",img)
            #cv2.waitKey(1)
            self.set_img()
            return [True,self.img]
    def set_img(self):
        """设置原始图片"""
        # 彩色图片转换
        # 将numpy数组转换为QPixmap
        height, width, channel = self.img.shape
        bytes_per_line = width * channel
        q_img = QImage(self.img.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        self.original_pixmap = QPixmap.fromImage(q_img)
        return self.original_pixmap