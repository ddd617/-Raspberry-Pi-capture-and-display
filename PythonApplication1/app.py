import cv2
import time

print("正在尝试打开摄像头...")
cap = cv2.VideoCapture(0)

# 获取摄像头的实际分辨率（非常重要，录像时必须用这个参数）
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30  # 设定录像帧率

if not cap.isOpened():
    print("错误：无法打开摄像头！请检查是否被其他软件占用。")
else:
    print(f"摄像头已连接。分辨率: {width}x{height}")
    print("操作指南：")
    print("  - 按 's' 键：拍照")
    print("  - 按 'r' 键：开始/停止 录像")
    print("  - 按 'q' 键：退出程序")

    # 初始化录像变量
    is_recording = False
    video_writer = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # --- 录像逻辑处理 ---
        if is_recording and video_writer is not None:
            video_writer.write(frame)
            # 在画面上显示 "REC" 红点提示正在录像
            cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 显示画面
        cv2.imshow('Camera Tool', frame)
        
        # 监听按键 (等待1毫秒)
        key = cv2.waitKey(1) & 0xFF
        
        # 1. 拍照功能 ('s')
        if key == ord('s'):
            filename = f"photo_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[系统] 照片已保存: {filename}")

        # 2. 录像开关功能 ('r')
        elif key == ord('r'):
            if not is_recording:
                # --- 开始录像 ---
                filename = f"video_{time.strftime('%Y%m%d_%H%M%S')}.avi"
                # 定义编码格式 (XVID 兼容性较好)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
                
                if video_writer.isOpened():
                    is_recording = True
                    print(f"[系统] 开始录像: {filename}")
                else:
                    print("[错误] 录像文件创建失败！")
            else:
                # --- 停止录像 ---
                is_recording = False
                if video_writer is not None:
                    video_writer.release()
                    video_writer = None
                    print("[系统] 录像已保存并停止。")

        # 3. 退出功能 ('q')
        elif key == ord('q'):
            break

    # 程序退出前的清理工作
    if is_recording and video_writer:
        video_writer.release()
    cap.release()
    cv2.destroyAllWindows()
    print("程序已安全退出。")