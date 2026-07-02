import cv2

class Camera:
    def __init__(self):
        # 0 代表默认摄像头
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("错误：无法打开摄像头！")
            
    def get_frame(self):
        """
        获取一帧画面
        增加了 ret 判断，确保只返回有效的图像数据
        """
        ret, frame = self.cap.read()
        
        # 只有读取成功(ret为True)且画面不为空时，才返回画面
        if ret and frame is not None:
            return frame
        else:
            # 如果读取失败（比如摄像头被遮挡或初始化中），返回None
            return None
            
    def release(self):
        """释放摄像头资源"""
        if self.cap.isOpened():
            self.cap.release()
            print("摄像头资源已释放")
