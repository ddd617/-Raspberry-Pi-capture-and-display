#!/usr/bin/env python3
"""
基于 GStreamer 的简单 RTSP 服务器（在树莓派上运行）。
依赖: gstreamer, gstreamer-rtsp-server, python-gi (PyGObject)

使用示例: python3 -m stream.rtsp_server
在浏览器/播放器中打开: rtsp://<pi-ip>:8554/test
"""
import os
import signal
import sys
import yaml

try:
    import gi
    gi.require_version('Gst', '1.0')
    gi.require_version('GstRtspServer', '1.0')
    from gi.repository import Gst, GstRtspServer, GObject
except Exception as e:
    print('无法导入 GStreamer Python 绑定 (gi). 请确保在树莓派上安装了 python3-gi, gir1.2-gst-rtsp-server-1.0 等。错误:', e)
    raise

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')

def load_config():
    cfg = {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        pass
    return cfg

class RTSPServer:
    def __init__(self, mount_point='/test'):
        Gst.init(None)
        self.server = GstRtspServer.RTSPServer()
        self.mount_point = mount_point

    def start(self, device=0, width=640, height=480, fps=30, bitrate=2000, port=8554):
        media_factory = GstRtspServer.RTSPMediaFactory()
        # 使用 v4l2src -> x264enc -> rtph264pay
        # 注意: 在某些平台上需要调整 encoder 参数 或 使用 hardware encoder
        device_path = f'/dev/video{device}' if isinstance(device, int) else str(device)
        launch_pipeline = (
            f"( v4l2src device={device_path} ! video/x-raw,width={width},height={height},framerate={fps}/1 "
            f"! videoconvert ! queue ! x264enc tune=zerolatency bitrate={bitrate} speed-preset=superfast "
            f"key-int-max={int(fps*2)} ! rtph264pay name=pay0 pt=96 )"
        )
        media_factory.set_launch(launch_pipeline)
        media_factory.set_shared(True)

        mounts = self.server.get_mount_points()
        mounts.add_factory(self.mount_point, media_factory)
        self.server.set_service(str(port))
        self.server.attach(None)
        print(f'RTSP server started at rtsp://0.0.0.0:{port}{self.mount_point}')

def _handle_sigterm(signum, frame):
    print('收到终止信号，退出')
    sys.exit(0)

if __name__ == '__main__':
    cfg = load_config()
    device = cfg.get('camera_device', 0)
    width = int(cfg.get('width', 640))
    height = int(cfg.get('height', 480))
    fps = int(cfg.get('fps', 30))
    bitrate = int(cfg.get('bitrate_kbps', 2000))
    port = int(cfg.get('rtsp_port', 8554))
    mount = cfg.get('rtsp_mount', '/test')

    signal.signal(signal.SIGINT, _handle_sigterm)
    signal.signal(signal.SIGTERM, _handle_sigterm)

    server = RTSPServer(mount_point=mount)
    try:
        server.start(device=device, width=width, height=height, fps=fps, bitrate=bitrate, port=port)
        # 运行 GObject 主循环以维持服务器
        loop = GObject.MainLoop()
        loop.run()
    except Exception as e:
        print('启动 RTSP 服务器失败:', e)
        sys.exit(1)
