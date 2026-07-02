import cv2
from capture import Camera  # 导入刚才写的模块

# 1. 启动摄像头
cam = Camera()
print("摄像头已启动，按 'q' 键退出...")

try:
    while True:
        # 2. 获取画面
        frame = cam.get_frame()
        
        # 【关键修改】必须确认 frame 不是 None 才能显示
        if frame is not None:
            cv2.imshow('My Modular Camera', frame)
        
        # 3. 按 'q' 键退出循环
        # waitKey(1) 表示等待1毫秒，保证画面流畅刷新
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
except KeyboardInterrupt:
    # 允许使用 Ctrl+C 强制停止程序
    print("\n检测到强制停止信号...")

finally:
    # 4. 无论怎么退出，都要执行清理工作
    cam.release()
    cv2.destroyAllWindows()
    print("程序已安全退出")
