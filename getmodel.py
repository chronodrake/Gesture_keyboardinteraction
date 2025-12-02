import mediapipe as mp
import os

# 初始化MediaPipe Hands，确保模型已下载
hands = mp.solutions.hands.Hands(static_image_mode=True)

# 获取MediaPipe的模型缓存目录
model_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "mediapipe", "models")
print("MediaPipe模型目录：", model_dir)

# 列出目录下的所有模型文件
if os.path.exists(model_dir):
    files = os.listdir(model_dir)
    print("目录下的模型文件：")
    for file in files:
        print(f"- {file}")
        # 打印文件绝对路径
        print(f"  绝对路径：{os.path.join(model_dir, file)}")
else:
    # 如果上述目录不存在，搜索其他可能路径
    print("未找到默认目录，尝试搜索其他路径...")
    # 可能的其他路径（MediaPipe旧版本/不同系统）
    possible_paths = [
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "mediapipe", "models"),
        os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "mediapipe", "models"),
        os.path.join(os.path.dirname(mp.__file__), "modules", "hands", "models"),  # 虚拟环境内
    ]
    for path in possible_paths:
        if os.path.exists(path):
            print(f"找到模型目录：{path}")
            for file in os.listdir(path):
                print(f"- {file}: {os.path.join(path, file)}")