import cv2
import time
import sys
import argparse
import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def main():
    cfg = load_config()
    default_url = cfg.get('rtsp_url', f"rtsp://127.0.0.1:{cfg.get('rtsp_port',8554)}{cfg.get('rtsp_mount','/test')}")

    parser = argparse.ArgumentParser(description='RTSP 客户端显示 (OpenCV)')
    parser.add_argument('--url', '-u', default=default_url, help='RTSP URL')
    parser.add_argument('--reconnect-delay', type=float, default=2.0, help='断线后重连等待秒数')
    args = parser.parse_args()

    url = args.url
    reconnect_delay = args.reconnect_delay

    print('打开 RTSP:', url)

    while True:
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if not cap or not cap.isOpened():
            print('无法打开流，等待重试...')
            time.sleep(reconnect_delay)
            continue

        fps_counter = 0
        start = time.time()
        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print('流中断，尝试重连...')
                    break
                fps_counter += 1
                elapsed = time.time() - start
                if elapsed > 0:
                    fps = fps_counter / elapsed
                else:
                    fps = 0.0
                # 显示 FPS
                cv2.putText(frame, f"FPS: {fps:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
                cv2.imshow('RTSP Client', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return
        finally:
            try:
                cap.release()
            except Exception:
                pass
            cv2.destroyAllWindows()
            time.sleep(reconnect_delay)

if __name__ == '__main__':
    main()
