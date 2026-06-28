部署说明

1. 将项目复制到树莓派（例如 /home/pi/stream）
2. 安装依赖：
   sudo apt update
   sudo apt install -y python3-pip python3-opencv v4l-utils
   sudo apt install -y python3-venv
   python3 -m pip install -r requirements.txt

3. 运行 MJPEG 服务器（测试）：
   python3 -m stream.http_mjpeg

4. 使用 systemd 安装服务：
   sudo cp deploy/raspberry_pi_stream.service /etc/systemd/system/raspberry_pi_stream.service
   sudo systemctl daemon-reload
   sudo systemctl enable raspberry_pi_stream.service
   sudo systemctl start raspberry_pi_stream.service

注意：若使用 RTSP 服务，需要在树莓派上安装 GStreamer、gst-rtsp-server 和 python3-gi。
