import cv2
import yaml
import time
import os

try:
    # picamera2 为树莓派上的替代高性能后端（可选）
    from picamera2 import Picamera2
    _HAS_PICAMERA2 = True
except Exception:
    Picamera2 = None
    _HAS_PICAMERA2 = False

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')

class CameraCapture:
    """通用摄像头捕获类，支持 OpenCV(V4L2) 和 picamera2（若可用）。

    参数:
    - device: OpenCV 设备索引或路径，或 None（从配置文件读取）
    - width, height, fps: 分辨率与帧率
    - backend: 可选 'auto'|'opencv'|'picamera2'，'auto' 将在可用时优先使用 picamera2
    """
    def __init__(self, device=None, width=640, height=480, fps=30, backend='auto'):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
        except Exception:
            cfg = {}

        self.device = device if device is not None else cfg.get('camera_device', 0)
        self.width = int(cfg.get('width', width))
        self.height = int(cfg.get('height', height))
        self.fps = int(cfg.get('fps', fps))
        self.backend = backend
        if self.backend == 'auto':
            self.backend = 'picamera2' if _HAS_PICAMERA2 else 'opencv'

        self._opencv_cap = None
        self._picam = None

    def start(self):
        if self.backend == 'picamera2' and _HAS_PICAMERA2:
            try:
                self._picam = Picamera2()
                cfg = self._picam.create_preview_configuration({'main': {'size': (self.width, self.height)}})
                self._picam.configure(cfg)
                self._picam.start()
                time.sleep(0.2)
                return
            except Exception as e:
                # 回退到 opencv
                print('picamera2 启动失败，回退到 OpenCV：', e)
                self.backend = 'opencv'

        # 使用 OpenCV V4L2 后端
        self._opencv_cap = cv2.VideoCapture(self.device, cv2.CAP_V4L2)
        self._opencv_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._opencv_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._opencv_cap.set(cv2.CAP_PROP_FPS, self.fps)
        time.sleep(0.5)

    def read(self):
        """返回 BGR 格式的 numpy 数组帧，失败时返回 None。"""
        if self.backend == 'picamera2' and self._picam is not None:
            try:
                frame = self._picam.capture_array()
                return frame
            except Exception:
                return None

        if self._opencv_cap is None:
            self.start()
        if self._opencv_cap is None:
            return None
        ret, frame = self._opencv_cap.read()
        if not ret:
            return None
        return frame

    def get_frame_jpeg(self, jpeg_quality=80):
        """返回 JPEG bytes，若失败返回 None。"""
        frame = self.read()
        if frame is None:
            return None
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)]
        ret, buf = cv2.imencode('.jpg', frame, encode_param)
        if not ret:
            return None
        return buf.tobytes()

    def frame_generator(self, jpeg_quality=80):
        """生成 JPEG bytes，用于 MJPEG 流。"""
        while True:
            jpg = self.get_frame_jpeg(jpeg_quality=jpeg_quality)
            if jpg is None:
                time.sleep(0.05)
                continue
            yield jpg

    def stop(self):
        if self._opencv_cap:
            try:
                self._opencv_cap.release()
            except Exception:
                pass
            self._opencv_cap = None
        if self._picam:
            try:
                self._picam.close()
            except Exception:
                try:
                    self._picam.stop()
                except Exception:
                    pass
            self._picam = None

    # 支持上下文管理
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()


if __name__ == '__main__':
    cam = CameraCapture()
    cam.start()
    try:
        for i in range(5):
            jpg = cam.get_frame_jpeg()
            if jpg:
                with open(f'test_{i}.jpg', 'wb') as f:
                    f.write(jpg)
            else:
                print('读取帧失败')
            time.sleep(0.1)
    finally:
        cam.stop()
