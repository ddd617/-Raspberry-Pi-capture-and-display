import time
import argparse
import cv2
from capture.capture import CameraCapture

parser = argparse.ArgumentParser(description='测试本地摄像头并测量 FPS')
parser.add_argument('--duration', type=float, default=5.0, help='测试时长（秒）')
args = parser.parse_args()

def main():
    cam = CameraCapture()
    cam.start()
    count = 0
    start = time.time()
    duration = args.duration
    try:
        while True:
            frame = cam.read()
            if frame is None:
                time.sleep(0.01)
                continue
            count += 1
            if time.time() - start >= duration:
                break
    finally:
        cam.stop()
    elapsed = time.time() - start
    fps = count / elapsed if elapsed > 0 else 0
    print(f'Tested frames: {count}, elapsed: {elapsed:.2f}s, avg FPS: {fps:.2f}')

if __name__ == '__main__':
    main()
