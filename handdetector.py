import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

class Handinteraction():
    def __init__(self,capset = (0,1280,720,60,1),con =0.8):
        self.cap = cv2.VideoCapture(capset[0])
        self.cap.set(3, capset[1])  # 宽度
        self.cap.set(4, capset[2])   # 高度
        self.cap.set(5, capset[3])    # 帧率（FPS）
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, capset[4])  # 缓冲区大小
        self.handtector = HandDetector(detectionCon=con,maxHands=1)        
        self.hands = None
        self.img = None
        self.hand = None
        self.lmlist = None
        self.vector = None
        self.cursor = None

    def _gethand(self):
        self.hands,self.img = self.handtector.findHands(self.img,flipType=1)
        if self.hands:
            self.hand =self.hands[0]
            self.lmlist = self.hand["lmList"]
    
    def _isactivate(self,threshold = 50):
        p1 = self.lmlist[8][:2]
        p2 = self.lmlist[12][:2]
        l,_,_ = self.handtector.findDistance(p1,p2,self.img)
        if l<threshold:
            return True
        else:
            return False
        
    def _getcursor(self):
        self.cursor = self.lmlist[8][:2]

    def _getway(self):
        p1 = np.array(self.lmlist[5][:2])
        p2 = np.array(self.lmlist[8][:2])
        self.vector = p2-p1
        if self.vector[0] ==0:
            tan = 100
        else:
            tan = self.vector[1]/self.vector[0]
        if abs(tan) > 1:  
            return [0, -1] if self.vector[1] > 0 else [0, 1]
        else:  
            return [1, 0] if self.vector[0] > 0 else [-1, 0]
    



    def update(self):
        self.is_work,self.img = self.cap.read()
        self.img = cv2.flip(self.img,1)
        if self.is_work:
            self._gethand()
            if self.hands:
                activate = self._isactivate()
                self._getcursor()
                way = self._getway()
                return True,activate,self.cursor,way
            else:
              # print("找   不  到  你  的  手")
                return True,None,None,None
        else:
           # print("摄像头未工作")
            return False,None,None,None


# handcontrol = Handinteraction()
# while True:
#     is_work,activate,cursor,way = handcontrol.update()
#     if is_work:
#         cv2.imshow("show",handcontrol.img)
#         print(activate,cursor,way)
#     else:
#         print("未有摄像头！")
#         break
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # 释放资源
# cv2.destroyAllWindows()
# handcontrol.cap.release()





