import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# ---------------------- 1. 手部检测封装类（负责摄像头+手部识别）----------------------
class HandDetection:
    """封装摄像头和手部检测逻辑，对外提供统一的“手部状态”接口"""
    def __init__(self, cam_width=1280, cam_height=720, fps=60):
        # 初始化摄像头参数
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, cam_width)
        self.cap.set(4, cam_height)
        self.cap.set(5, fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少延迟

        # 初始化手部检测器
        self.detector = HandDetector(
            detectionCon=0.8,
            trackCon=0.7,
            maxHands=1,
            modelComplexity=0
        )

    def get_hand_state(self):
        """获取手部状态：(是否成功读取画面, 画面帧, 指尖坐标, 是否处于拖动状态)"""
        success, frame = self.cap.read()
        if not success:
            return False, None, None, False  # 读取失败

        # 镜像翻转画面（符合人眼习惯）
        frame = cv2.flip(frame, flipCode=1)
        # 检测手部
        hands, frame = self.detector.findHands(frame, flipType=False)

        cursor = None  # 指尖坐标 (x,y)
        is_dragging = False  # 是否处于拖动状态（手指闭合）

        if hands:
            hand = hands[0]
            lm_list = hand["lmList"]
            # 取食指指尖（8号关键点）和无名指指尖（12号关键点）
            index_tip = lm_list[8][:2]
            ring_tip = lm_list[12][:2]
            # 计算两指尖距离，判断是否闭合（拖动状态）
            distance, _, _ = self.detector.findDistance(index_tip, ring_tip, frame)
            cursor = index_tip
            is_dragging = distance < 30  # 阈值可调整

            # 绘制拖动光标（红色圆点，提升用户体验）
            if is_dragging:
                cv2.circle(frame, cursor, 8, (0, 0, 255), -1)

        return True, frame, cursor, is_dragging

    def release(self):
        """释放摄像头资源（析构时调用）"""
        self.cap.release()
        cv2.destroyAllWindows()

# ---------------------- 2. 可拖动矩形类（负责单个矩形的属性和行为）----------------------
class DraggableRect:
    """封装可拖动矩形的属性（位置、大小、颜色）和行为（更新、绘制）"""
    def __init__(self, pos_center, size=[100, 100], smooth_window=3):
        self.pos_center = pos_center  # 中心点坐标 (x,y)
        self.size = size  # 宽高 [w, h]
        self.smooth_window = smooth_window  # 坐标平滑窗口大小
        self.history_cursor = []  # 平滑用的历史坐标队列
        self.color_default = (255, 0, 255)  # 未选中颜色（洋红）
        self.color_selected = (0, 255, 0)   # 选中颜色（绿色）
        self.current_color = self.color_default  # 当前颜色

    def _is_cursor_inside(self, cursor):
        """私有方法：判断光标是否在矩形内（内部逻辑，不对外暴露）"""
        w, h = self.size
        x1 = self.pos_center[0] - w // 2
        y1 = self.pos_center[1] - h // 2
        x2 = self.pos_center[0] + w // 2
        y2 = self.pos_center[1] + h // 2
        return x1 < cursor[0] < x2 and y1 < cursor[1] < y2

    def _smooth_cursor(self, cursor):
        """私有方法：坐标平滑处理（内部逻辑，不对外暴露）"""
        self.history_cursor.append(cursor)
        # 只保留最近N帧坐标，避免延迟
        if len(self.history_cursor) > self.smooth_window:
            self.history_cursor.pop(0)
        return np.mean(self.history_cursor, axis=0).astype(int)

    def _clamp_position(self, pos):
        """私有方法：限制矩形位置，避免拖出屏幕（内部逻辑，不对外暴露）"""
        w, h = self.size
        x = max(w//2, min(self.cam_width - w//2, pos[0]))  # x轴边界
        y = max(h//2, min(self.cam_height - h//2, pos[1]))  # y轴边界
        return (x, y)

    def update(self, frame, cursor, is_dragging):
        """公有方法：更新矩形状态（对外暴露的唯一接口）"""
        # 绑定屏幕尺寸（从frame获取，避免硬编码）
        self.cam_width = frame.shape[1]
        self.cam_height = frame.shape[0]

        if is_dragging and cursor is not None:
            # 光标在矩形内 → 选中状态
            if self._is_cursor_inside(cursor):
                self.current_color = self.color_selected
                # 平滑坐标并更新位置
                smooth_pos = self._smooth_cursor(cursor)
                self.pos_center = self._clamp_position(smooth_pos)
            else:
                self.current_color = self.color_default
                self.history_cursor.clear()  # 未选中时清空平滑队列
        else:
            # 未拖动 → 重置状态
            self.current_color = self.color_default
            self.history_cursor.clear()

        # 绘制矩形（与选中判断区域完全一致）
        self._draw(frame)

    def _draw(self, frame):
        """私有方法：绘制矩形（内部逻辑，不对外暴露）"""
        w, h = self.size
        x1 = self.pos_center[0] - w // 2
        y1 = self.pos_center[1] - h // 2
        x2 = self.pos_center[0] + w // 2
        y2 = self.pos_center[1] + h // 2
        # 填充矩形 + 白色边框（清晰可见）
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.current_color, cv2.FILLED)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

# ---------------------- 3. 主应用类（整合所有模块，负责整体逻辑）----------------------
class GestureDragApp:
    """主应用类：初始化所有组件，运行主循环"""
    def __init__(self):
        # 初始化手部检测模块
        self.hand_detector = HandDetection()
        # 初始化可拖动矩形列表（4个矩形，均匀分布）
        self.rects = self._init_rects()

    def _init_rects(self):
        """初始化4个可拖动矩形（内部逻辑）"""
        positions = [(300, 200), (900, 200), (300, 500), (900, 500)]
        return [DraggableRect(pos, size=[100, 100]) for pos in positions]

    def run(self):
        """运行主循环（对外暴露的启动接口）"""
        print("应用启动，按ESC键退出...")
        while True:
            # 1. 获取手部状态
            success, frame, cursor, is_dragging = self.hand_detector.get_hand_state()
            if not success:
                print("摄像头读取失败！")
                break

            # 2. 更新所有矩形状态
            for rect in self.rects:
                rect.update(frame, cursor, is_dragging)

            # 3. 显示画面
            cv2.imshow("Gesture Drag App", frame)

            # 4. 退出逻辑（按ESC键）
            if cv2.waitKey(1) & 0xFF == 27:
                break

        # 5. 退出时释放资源
        self.hand_detector.release()
        print("应用已退出")

# ---------------------- 程序入口 ----------------------
if __name__ == "__main__":
    # 初始化并启动应用
    app = GestureDragApp()
    app.run()