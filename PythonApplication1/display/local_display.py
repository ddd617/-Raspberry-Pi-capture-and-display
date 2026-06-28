import cv2
import time
from capture.capture import CameraCapture

def main():
    cam = CameraCapture()
    cam.start()
    try:
        while True:
            frame = cam.read()
            if frame is None:
                time.sleep(0.05)
                continue
            cv2.imshow('Local Display', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam.stop()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
