import json
import time
import os
import sys
import subprocess
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from curl_cffi import requests
import whisper

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
}

OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载已有视频数据
with open("./output/douyin_videos.json", "r", encoding="utf-8") as f:
    videos = json.load(f)

print(f"已加载 {len(videos)} 条视频数据")

# 选第一条有文案的视频
test_video = None
for v in videos:
    if v.get("video_play_url") and v.get("desc"):
        test_video = v
        break

if not test_video:
    print("无可用视频")
    sys.exit(1)

aweme_id = test_video["aweme_id"]
play_url = test_video["video_play_url"]
desc = test_video["desc"]

print(f"\n测试视频: [{aweme_id}] {desc[:60]}")
print(f"视频URL: {play_url[:100]}...")

# Step 1: 下载视频
video_path = os.path.join(OUTPUT_DIR, f"{aweme_id}.mp4")
if not os.path.exists(video_path):
    print(f"\n[Step 1] 下载视频...")
    try:
        r = requests.get(play_url, headers=HEADERS, impersonate="chrome131", timeout=60)
        if r.status_code == 200 and len(r.content) > 10000:
            with open(video_path, "wb") as f:
                f.write(r.content)
            size_mb = len(r.content) / 1024 / 1024
            print(f"  [OK] 下载成功: {size_mb:.1f} MB")
        else:
            print(f"  [FAIL] 状态码: {r.status_code}, 大小: {len(r.content)}")
            # 尝试重新获取视频 URL
            print(f"  [尝试] 重新获取视频URL...")
            from check_fields import COOKIES, API_HEADERS
            session = requests.Session()
            params = {
                "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
                "sec_user_id": "MS4wLjABAAAA1-M5ZigLVjWEc2LDSKa-4Sm28o0kTSzJOQ0YMbk4EFW_83PMw0dLCKZ2ibLVoOqH",
                "max_cursor": "0", "count": "5", "publish_video_strategy_type": "2",
                "version_code": "170400", "version_name": "17.4.0", "cookie_enabled": "true",
            }
            resp = session.get("https://www.douyin.com/aweme/v1/web/aweme/post/",
                               params=params, headers=API_HEADERS, cookies=COOKIES,
                               impersonate="chrome131", timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                for a in data.get("aweme_list", []):
                    if a.get("aweme_id") == aweme_id:
                        new_url = _extract_play_url(a)
                        if new_url:
                            play_url = new_url
                            print(f"  [OK] 获取到新URL")
                            r2 = requests.get(play_url, headers=HEADERS, impersonate="chrome131", timeout=60)
                            if r2.status_code == 200 and len(r2.content) > 10000:
                                with open(video_path, "wb") as f2:
                                    f2.write(r2.content)
                                print(f"  [OK] 重新下载成功")
                            break
    except Exception as e:
        print(f"  [FAIL] {e}")
else:
    print(f"\n[Step 1] 视频已存在: {video_path}")

# Step 2: 提取音频
audio_path = os.path.join(OUTPUT_DIR, f"{aweme_id}.wav")
if not os.path.exists(audio_path) and os.path.exists(video_path):
    print(f"\n[Step 2] 提取音频 (16kHz mono)...")
    result = subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-ac", "1", "-ar", "16000", "-f", "wav",
        audio_path,
    ], capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = os.path.getsize(audio_path) / 1024 / 1024
        print(f"  [OK] 音频提取成功: {size_mb:.1f} MB")
    else:
        print(f"  [FAIL] {result.stderr[:300]}")
        sys.exit(1)
elif os.path.exists(audio_path):
    print(f"\n[Step 2] 音频已存在: {audio_path}")

# Step 3: Whisper 语音识别
print(f"\n[Step 3] Whisper 语音识别...")
if os.path.exists(audio_path):
    model = whisper.load_model("base")  # tiny/base/small/medium/large
    result = model.transcribe(audio_path, language="zh", verbose=False)
    transcription = result["text"].strip()
    print(f"  [OK] 识别完成!")
    print(f"  {'='*50}")
    print(f"  口播文案: {transcription}")
    print(f"  {'='*50}")

    # 保存结果
    result_path = os.path.join(OUTPUT_DIR, f"{aweme_id}_transcript.txt")
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(f"视频ID: {aweme_id}\n")
        f.write(f"标题: {desc}\n")
        f.write(f"口播文案:\n{transcription}\n")
    print(f"  [OK] 已保存: {result_path}")
else:
    print(f"  [FAIL] 无音频文件")


def _extract_play_url(aweme):
    video = aweme.get("video", {})
    play_addr = video.get("play_addr", {})
    url_list = play_addr.get("url_list", [])
    if url_list:
        return url_list[0]
    bit_rate = video.get("bit_rate", [])
    if bit_rate:
        url_list_br = bit_rate[0].get("play_addr", {}).get("url_list", [])
        if url_list_br:
            return url_list_br[0]
    return ""
