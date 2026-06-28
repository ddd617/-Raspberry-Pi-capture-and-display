"""
测量 MJPEG 流端到端延迟的脚本。
要求：服务端在每个 multipart 部分包含 `X-Timestamp: <unix_seconds>` 头（本项目的 http_mjpeg 已实现）。
用法示例：
 python3 stream/measure_latency_mjpeg.py --url http://raspberrypi:5000/video_feed --count 100

输出：显示 min/median/mean/max 延迟（秒）以及每帧延迟的简要日志。
"""
import requests
import argparse
import time
import sys
import os
import statistics

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')

parser = argparse.ArgumentParser(description='测量 MJPEG 流的网络延迟')
parser.add_argument('--url', '-u', default=None, help='MJPEG 流 URL, 例如 http://ip:5000/video_feed')
parser.add_argument('--count', '-n', type=int, default=100, help='采样帧数')
parser.add_argument('--timeout', type=float, default=10.0, help='HTTP 请求超时（秒）')
args = parser.parse_args()

if args.url is None:
    # 从配置文件构造默认 URL
    try:
        import yaml
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
        host = cfg.get('host', '127.0.0.1')
        port = cfg.get('server_port', 5000)
        args.url = f'http://{host}:{port}/video_feed'
    except Exception:
        print('请提供 --url 或确保 config/config.yaml 可用')
        sys.exit(1)

print('测量目标 URL:', args.url)

resp = requests.get(args.url, stream=True, timeout=args.timeout)
if resp.status_code != 200:
    print('无法打开流，HTTP 状态:', resp.status_code)
    sys.exit(1)

boundary = b'--frame'
buffer = b''
latencies = []
count = args.count
seen = 0
start_time = time.time()

try:
    for chunk in resp.iter_content(chunk_size=4096):
        if not chunk:
            continue
        buffer += chunk
        # 查找 JPEG 起始和结束标记
        while True:
            start_idx = buffer.find(b'\xff\xd8')
            end_idx = buffer.find(b'\xff\xd9', start_idx + 2) if start_idx != -1 else -1
            if start_idx != -1 and end_idx != -1:
                jpg = buffer[start_idx:end_idx+2]
                # 找到最近的 boundary 在 jpg 之前，用于解析头部
                bidx = buffer.rfind(boundary, 0, start_idx)
                headers = b''
                if bidx != -1:
                    headers_end = start_idx
                    headers = buffer[bidx:start_idx]
                # 从 headers 中解析 X-Timestamp
                ts = None
                try:
                    # 将 headers 解码为文本并按行解析
                    text = headers.decode('utf-8', errors='ignore')
                    for line in text.split('\r\n'):
                        if line.lower().startswith('x-timestamp:'):
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                ts = float(parts[1].strip())
                                break
                except Exception:
                    ts = None
                recv_time = time.time()
                if ts is not None:
                    lat = recv_time - ts
                    latencies.append(lat)
                    seen += 1
                    if seen % max(1, count//10) == 0 or seen <= 5:
                        print(f'#{seen}: latency={lat*1000:.1f} ms')
                # 移除已处理的数据
                buffer = buffer[end_idx+2:]
                if seen >= count:
                    raise StopIteration
                # 继续查找同一 buffer 中的下一帧
                continue
            break
except StopIteration:
    pass
except Exception as e:
    print('读取流时出错:', e)
finally:
    try:
        resp.close()
    except Exception:
        pass

if len(latencies) == 0:
    print('未收到带时间戳的帧，无法统计')
    sys.exit(1)

print('\n样本数:', len(latencies))
print('min: %.1f ms' % (min(latencies)*1000))
print('median: %.1f ms' % (statistics.median(latencies)*1000))
print('mean: %.1f ms' % (statistics.mean(latencies)*1000))
print('max: %.1f ms' % (max(latencies)*1000))
print('总耗时: %.2fs' % (time.time() - start_time))
