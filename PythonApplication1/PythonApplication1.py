from flask import Flask, Response, render_template
import cv2

# 初始化 Flask 应用
app = Flask(__name__)

# 初始化摄像头
# cv2.CAP_DSHOW 是 Windows 下解决黑屏的关键参数
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# 强制设置分辨率，防止因默认分辨率过高导致读取失败
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def generate_frames():
    """生成视频流的生成器函数"""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # 将帧编码为 JPEG 格式
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # 按照 MJPEG 流格式输出
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """主页路由，返回 HTML 页面"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """视频流路由，返回实时画面"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # host='0.0.0.0' 允许局域网访问（如手机访问）
    # debug=True 开启调试模式，修改代码后自动重启
    app.run(host='0.0.0.0', port=5000, debug=True)