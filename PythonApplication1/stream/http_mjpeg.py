from flask import Flask, Response, render_template_string
import threading
import os
import yaml
import signal
import sys
import time
from capture.capture import CameraCapture

app = Flask(__name__)

HTML_INDEX = """
<html>
  <head>
    <title>Raspberry Pi MJPEG Stream</title>
  </head>
  <body>
    <h1>MJPEG Stream</h1>
    <img src="/video_feed" />
  </body>
</html>
"""

# 读取配置
cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
_port = 5000
_jpeg_quality = 80
_try_cfg = {}
try:
    with open(cfg_path, 'r', encoding='utf-8') as f:
        _try_cfg = yaml.safe_load(f) or {}
        _port = int(_try_cfg.get('server_port', _port))
        _jpeg_quality = int(_try_cfg.get('jpeg_quality', _jpeg_quality))
except Exception:
    pass

camera = CameraCapture(backend='auto')

def gen_frames():
    # yields multipart JPEG frames，附加 X-Timestamp 头（Unix 秒，浮点数）以便测量延迟
    for jpg in camera.frame_generator(jpeg_quality=_jpeg_quality):
        ts = time.time()
        ts_header = f'X-Timestamp: {ts:.6f}\r\n'.encode('utf-8')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n' + ts_header + b'\r\n' + jpg + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_INDEX)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return {'ok': True, 'backend': camera.backend, 'resolution': f'{camera.width}x{camera.height}', 'fps': camera.fps}

def _handle_sigterm(signum, frame):
    print('收到终止信号，正在停止摄像头并退出')
    try:
        camera.stop()
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, _handle_sigterm)
signal.signal(signal.SIGTERM, _handle_sigterm)

if __name__ == '__main__':
    try:
        camera.start()
        print(f'Started camera using backend={camera.backend}, listening on port {_port}')
        # 禁用 reloader 以避免双重启动摄像头
        app.run(host='0.0.0.0', port=_port, threaded=True, use_reloader=False)
    except Exception as e:
        print('服务器运行时出错:', e)
    finally:
        camera.stop()
