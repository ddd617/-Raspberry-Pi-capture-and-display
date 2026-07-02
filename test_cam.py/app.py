from flask import Flask, Response
from capture import Camera  # 导入我们写好的模块
import cv2

app = Flask(__name__)

# 1. 实例化摄像头（全局只需要一个摄像师）
camera = Camera()

def generate_frames():
    """
    这是一个生成器函数
    它会不断地从摄像头获取画面，并转换成网页能显示的格式
    """
    while True:
        frame = camera.get_frame()
        
        if frame is not None:
            # 【关键】将图片压缩成 JPEG 格式
            # OpenCV 默认是 BGR，虽然浏览器通常能识别，但标准做法是转 RGB，
            # 不过为了性能和简单，这里直接编码通常也没问题。
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # 按照 HTTP 协议格式输出数据流
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def video_feed():
    """
    网页的主路由
    返回一个特殊的响应，告诉浏览器：“我要给你发连续的图片流”
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Web 服务器启动中... 请访问 http://127.0.0.1:5000")
    # debug=True 方便调试，host='0.0.0.0' 允许局域网访问（可选）
    app.run(host='0.0.0.0', port=5000, debug=True)

