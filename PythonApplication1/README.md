基于树莓派的实时视频流捕获与显示系统

说明
- 使用 OpenCV 捕获摄像头帧（可替换为 libcamera / picamera2 实现以获得更好性能）。
- 提供一个快速的 HTTP MJPEG 预览服务器（Flask）。

快速开始
1. 在树莓派上安装依赖：
   python3 -m pip install -r requirements.txt
2. 配置参数：编辑 config/config.yaml
3. 启动 MJPEG 服务器：
   python3 -m stream.http_mjpeg
4. 在浏览器中打开：http://<raspberry-pi-ip>:5000/

后续
- 可替换 capture 模块为 libcamera/picamera2 或者用 GStreamer 实现低延迟 H.264 发布。
- 若需浏览器端低延迟推荐使用 WebRTC。