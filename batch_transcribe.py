import json
import time
import os
import sys
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from curl_cffi import requests
import whisper

SEC_UID = "MS4wLjABAAAA1-M5ZigLVjWEc2LDSKa-4Sm28o0kTSzJOQ0YMbk4EFW_83PMw0dLCKZ2ibLVoOqH"

COOKIES = {
    "ttwid": "1%7CRDTFK5j3ruZz_KMefSXijbHOU7PwgAPITRfvsIfDhnQ%7C1778144413%7C1ecc27ffdcc7039cf117104248868068e143e8cc6ae7e6f5079b174de895111c",
    "sessionid": "b219ac1328a798534e1b2147030ff9a1",
    "sessionid_ss": "b219ac1328a798534e1b2147030ff9a1",
    "sid_tt": "b219ac1328a798534e1b2147030ff9a1",
    "uid_tt": "00e9b56bae643171b0e2bf62375fe122",
    "passport_csrf_token": "192265dbbcaeba987f829399e90b3eb4",
    "passport_csrf_token_default": "192265dbbcaeba987f829399e90b3eb4",
    "passport_mfa_token": "CjXnpd9q%2FggRh0djuahjauCla%2FKUGnLM%2Fz3nEXj0Yp%2FdoMwH%2FX46z3NjMXaq2KpwEAWgRerfTRpKCjwAAAAAAAAAAAAAUGRB%2FD5V3VHPy2G7OEz2e%2Br08SMCCv45XzWO7nxjEBcknyC%2B%2Bamt%2B7ZaMPJGBOWDCrAQiemQDhj2sdFsIAIiAQNU1lkF",
}

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
}

DL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
}

OUTPUT_DIR = "./output/transcripts"
VIDEO_DIR = "./output/videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

session = requests.Session()

print("=" * 60)
print("  批量口播转写工具")
print("=" * 60)

# ====== Step 1: 重新拉取视频URL列表 ======
print(f"\n[1] 重新获取视频URL列表（旧URL已过期）...")

all_videos = []
max_cursor = 0
has_more = True
page = 0

while has_more and page < 15:
    page += 1
    params = {
        "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
        "sec_user_id": SEC_UID, "max_cursor": str(max_cursor), "count": "20",
        "publish_video_strategy_type": "2", "version_code": "170400",
        "version_name": "17.4.0", "cookie_enabled": "true",
        "screen_width": "1920", "screen_height": "1080",
    }
    resp = session.get(
        "https://www.douyin.com/aweme/v1/web/aweme/post/",
        params=params, headers=API_HEADERS, cookies=COOKIES,
        impersonate="chrome131", timeout=20,
    )
    if resp.status_code != 200:
        print(f"  状态码异常: {resp.status_code}")
        break

    data = resp.json()
    if data.get("status_code") != 0:
        print(f"  API 错误: {data.get('status_msg')}")
        break

    aweme_list = data.get("aweme_list", [])
    if not aweme_list:
        break

    for a in aweme_list:
        # 提取无水印视频URL
        video = a.get("video", {})
        play_addr = video.get("play_addr", {})
        url_list = play_addr.get("url_list", [])
        play_url = url_list[0] if url_list else ""

        if not play_url:
            bit_rate = video.get("bit_rate", [])
            if bit_rate:
                url_list_br = bit_rate[0].get("play_addr", {}).get("url_list", [])
                if url_list_br:
                    play_url = url_list_br[0]

        desc = a.get("desc", "")
        aweme_id = a.get("aweme_id", "")

        if play_url and aweme_id:
            all_videos.append({
                "aweme_id": aweme_id,
                "desc": desc,
                "video_url": play_url,
                "duration": a.get("duration", 0),
            })

    max_cursor = data.get("max_cursor", 0)
    has_more = data.get("has_more", 0) == 1 and len(aweme_list) > 0
    print(f"  第{page}页: {len(aweme_list)}条, 累计{len(all_videos)}条")

    if has_more:
        time.sleep(1)

print(f"  共获取 {len(all_videos)} 条有效视频URL")

# ====== Step 2: 加载 Whisper 模型 ======
print(f"\n[2] 加载 Whisper 模型 (base)...")
model = whisper.load_model("base")
print(f"  [OK] 模型加载完成")

# ====== Step 3: 逐条处理 ======
print(f"\n[3] 开始批量转写...")
success_count = 0
skip_count = 0
fail_count = 0
results = []

for i, v in enumerate(all_videos):
    aweme_id = v["aweme_id"]
    desc = v["desc"]
    play_url = v["video_url"]

    # 跳过已处理的
    transcript_path = os.path.join(OUTPUT_DIR, f"{aweme_id}.txt")
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as f:
            existing = f.read()
            if existing.strip():
                skip_count += 1
                results.append({"aweme_id": aweme_id, "desc": desc, "transcript": existing.strip()})
                continue

    print(f"\n  [{i+1}/{len(all_videos)}] {aweme_id}")
    print(f"    标题: {desc[:60]}")

    # 下载视频
    video_path = os.path.join(VIDEO_DIR, f"{aweme_id}.mp4")
    if not os.path.exists(video_path) or os.path.getsize(video_path) < 10000:
        try:
            r = requests.get(play_url, headers=DL_HEADERS, impersonate="chrome131", timeout=120)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(video_path, "wb") as f:
                    f.write(r.content)
                print(f"    下载: {len(r.content)/1024/1024:.1f}MB")
            else:
                print(f"    下载失败: status={r.status_code}")
                fail_count += 1
                continue
        except Exception as e:
            print(f"    下载异常: {e}")
            fail_count += 1
            continue

    # 提取音频
    audio_path = os.path.join(VIDEO_DIR, f"{aweme_id}.wav")
    if not os.path.exists(audio_path):
        result = subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "1", "-ar", "16000", "-f", "wav", audio_path,
        ], capture_output=True)
        if result.returncode != 0:
            print(f"    音频提取失败")
            fail_count += 1
            continue

    # Whisper 转写
    try:
        trans = model.transcribe(audio_path, language="zh", verbose=False)
        transcript = trans["text"].strip()
        print(f"    口播: {transcript[:100]}...")

        # 保存
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        results.append({"aweme_id": aweme_id, "desc": desc, "transcript": transcript})
        success_count += 1

        # 清理视频和音频（节省空间）
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        print(f"    转写异常: {e}")
        fail_count += 1

    print(f"    进度: 成功{success_count} 跳过{skip_count} 失败{fail_count}")

# ====== Step 4: 保存汇总 ======
print(f"\n[4] 保存汇总结果...")

# JSON 汇总
summary_path = os.path.join("./output", "douyin_transcripts.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 纯文本汇总
txt_path = os.path.join("./output", "douyin_transcripts.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    for i, r in enumerate(results, 1):
        f.write(f"{'='*60}\n")
        f.write(f"第{i}条  [{r['aweme_id']}]\n")
        f.write(f"标题: {r['desc']}\n")
        f.write(f"口播: {r['transcript']}\n\n")

print(f"\n{'='*60}")
print(f"  转写完成!")
print(f"  成功: {success_count} | 跳过: {skip_count} | 失败: {fail_count}")
print(f"  总计: {len(results)} 条")
print(f"  JSON: {summary_path}")
print(f"  TXT:  {txt_path}")
print(f"{'='*60}")
