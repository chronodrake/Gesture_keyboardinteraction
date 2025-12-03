from cvzone.HandTrackingModule import HandDetector
import cv2
import time
import socket 
import numpy as np

class SocketClient:
    def __init__(self, host="127.0.0.1", port=8888):
        """
        初始化socket客户端
        :param host: 服务端地址
        :param port: 端口
        """
        self.host = host  # Unity 服务端IP
        self.port = port #端口
        self.socket = None
        self.connected = False
        self.reconnect_interval = 2  # 断线重连间隔

    def connect(self):
        """建立连接"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3)  # 连接超时时间
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"连接 Unity 服务端成功（{self.host}:{self.port}）")
        except Exception as e:
            self.connected = False
            print(f"连接失败：{e}，{self.reconnect_interval}秒后重试...")
            time.sleep(self.reconnect_interval)

    def send_data(self, data):
        """发送数据（字符串格式）"""
        if not self.connected:
            self.connect()  # 断线自动重连
            return
        
        try:
            # 编码为 UTF-8 发送（Unity 端对应解码）
            self.socket.sendall((data + "\n").encode("utf-8"))  # 加\n作为结束符
        except Exception as e:
            self.connected = False
            print(f" 发送失败：{e}")

    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print(" 连接已关闭")
            

class Handinteraction():
    def __init__(self,capset = (0,1280,720,60,1),con =0.8):
        """
        检测器
        :param capset: 一个元组，第一个表示用什么摄像头，第二个宽度，第三个高度，第四个帧率
        :param con: 置信度阈值
        """
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
            return [1, 0] if self.vector[0] > 0 else [-1, 0]#获得手势方向
        
    def update(self):
        """该类的update方法返回了四个对象：bool对象，表示摄像头是否正常工作，是否激活，指针位置，手势横纵坐标"""
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

if __name__ == "__main__":
    # 初始化手势识别和 Socket 客户端
    hand_interaction = Handinteraction()
    socket_client = SocketClient(host="127.0.0.1", port=8888)  
    socket_client.connect()  #

    # 发送频率控制（30次/秒，与Unity帧率匹配）
    send_interval = 1 / 30
    last_send_time = time.time()

    try:
        while True:
            # 1. 获取手势数据
            iswork,activate, _, way = hand_interaction.update()
            if activate is None or way is None:
                activate = False  # 未检测到手，标记为未激活
                way = [0, 0]     # 未检测到手，方向设为无
            
            # 2. 按固定格式拼接数据（激活状态|X|Y）q
            data = f"{activate}|{way[0]}|{way[1]}"
            
            # 3. 控制发送频率（避免数据堆积）
            current_time = time.time()
            if current_time - last_send_time >= send_interval:
                socket_client.send_data(data)
                print(f"发送数据：{data}")
                last_send_time = current_time
            
            # 4. 显示调试画面
            cv2.imshow("Gesture Capture", hand_interaction.img)
            
            # 5. 按 Q 退出
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        print("\n程序手动退出")
    finally:
        # 释放资源
        socket_client.close()
        hand_interaction.cap.release()
        cv2.destroyAllWindows()
