import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
class dragRect():
    def __init__(self,posCenter,size=[200,200],smooth_window = 3):
        self.colorR = 255,0,255
        self.history_cursor = []
        self.posCenter = posCenter
        self.size = size
        self.smooth_window = smooth_window
    def update(self,cursor = None,avaible=False):
        if avaible:
            self.history_cursor.append(cursor)#建立历史坐标数组
            if len(self.history_cursor) > self.smooth_window:
                self.history_cursor.pop(0)
            smooth_cursor = np.mean(self.history_cursor, axis=0).astype(int)
            w, h = self.size
            x1 = self.posCenter[0] - w // 2
            y1 = self.posCenter[1] - h // 2
            x2 = self.posCenter[0] + w // 2
            y2 = self.posCenter[1] + h // 2
            # 判断指尖是否在矩形内
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.colorR = (0, 255, 0)  # 选中：绿色
                self.posCenter = smooth_cursor  # 用平滑后的坐标更新矩形
            else:
                self.colorR = (255, 0, 255)  # 未选中：洋红
        else:
            self.history_cursor = []
            self.colorR = (255, 0, 255)
        cv2.rectangle(img,(self.posCenter[0]-self.size[0]//2, self.posCenter[1]-self.size[1]), 
              (self.posCenter[0]+self.size[0]//2, self.posCenter[1]+self.size[1]//2), self.colorR, cv2.FILLED)
        

cap = cv2.VideoCapture(0)

cap.set(3, 1280)  # 宽度
cap.set(4, 720)   # 高度
cap.set(5, 60)    # 帧率（FPS）
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 缓冲区大小设为1，减少延迟
detector = HandDetector(detectionCon=0.8)
dragRectlist = []
dragRectlist = []
# 矩形位置：x=300/900（左右两列），y=200/500（上下两行），避免重叠和超出画面
positions = [(300, 200), (900, 200), (300, 500), (900, 500)]
for pos in positions:
    dragRectlist.append(dragRect(pos, size=[100, 100]))

while True:
    success,img = cap.read()
    if not success:
        print("未找到您设备的摄像头！")
        break
    img = cv2.flip(img,flipCode=1)
    hands,img = detector.findHands(img,flipType=False)

    #hands是一个由字典组成的列表，字典表示一只手
        # [{'lmList': [[889, 652, 0], [807, 613, -25], [753, 538, -39], [723, 475, -52], [684, 431, -66], [789, 432, -27],
    #              [762, 347, -56], [744, 295, -78], [727, 248, -95], [841, 426, -39], [835, 326, -65], [828, 260, -89],
    #              [820, 204, -106], [889, 445, -54], [894, 356, -85], [892, 295, -107], [889, 239, -123],
    #              [933, 483, -71], [957, 421, -101], [973, 376, -115], [986, 334, -124]], 'bbox': (684, 204, 302, 448),
    #   'center': (835, 428), 'type': 'Right'}]
    # 如果能检测到手那么就进行下一步
    cursor = None
    avaible = False
    if hands:
        hand = hands[0]#取右手（视频反转手型相反）
        position = hand["lmList"]
        p1 = position[8][0:2]  # 第8个关键点（食指指尖）
        p2 = position[12][0:2] # 第12个关键点（无名指指尖）
        l,_,_ = detector.findDistance(p1,p2,img)
        cursor = position[8][0:2]
        if l<50:
            avaible = True
        else:
            avaible = False
        if avaible:
            cv2.circle(img, cursor, 8, (0, 0, 255), -1)
        t=0
        for i in position: 
            cv2.putText(img,text=f"{t}",org = i[0:2],fontFace=1,fontScale=1,color=(255,255,255))    
            t=t+1

    for rect in dragRectlist:
        rect.update(cursor,avaible)
    cv2.imshow("image",img)
    if cv2.waitKey(1) & 0xFF == 27:
        break


