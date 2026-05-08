import json
import time
import os
import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from curl_cffi import requests

SEC_UID = "MS4wLjABAAAA1-M5ZigLVjWEc2LDSKa-4Sm28o0kTSzJOQ0YMbk4EFW_83PMw0dLCKZ2ibLVoOqH"

COOKIES = {
    "ttwid": "1%7CRDTFK5j3ruZz_KMefSXijbHOU7PwgAPITRfvsIfDhnQ%7C1778144413%7C1ecc27ffdcc7039cf117104248868068e143e8cc6ae7e6f5079b174de895111c",
    "sessionid": "b219ac1328a798534e1b2147030ff9a1",
    "sessionid_ss": "b219ac1328a798534e1b2147030ff9a1",
    "sid_tt": "b219ac1328a798534e1b2147030ff9a1",
    "uid_tt": "00e9b56bae643171b0e2bf62375fe122",
    "passport_csrf_token": "192265dbbcaeba987f829399e90b3eb4",
}

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
}

session = requests.Session()

# 先用 post API 拿一条完整数据
print("=" * 60)
print("  检查抖音 API 口播/字幕字段")
print("=" * 60)

params = {
    "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
    "sec_user_id": SEC_UID, "max_cursor": "0", "count": "1",
    "publish_video_strategy_type": "2", "version_code": "170400",
    "version_name": "17.4.0", "cookie_enabled": "true",
    "screen_width": "1920", "screen_height": "1080",
}

r = session.get(
    "https://www.douyin.com/aweme/v1/web/aweme/post/",
    params=params, headers=API_HEADERS, cookies=COOKIES,
    impersonate="chrome131", timeout=20,
)

if r.status_code != 200:
    print(f"  状态码: {r.status_code}")
    print(f"  响应: {r.text[:300]}")
    sys.exit(1)

data = r.json()
aweme_list = data.get("aweme_list", [])

if not aweme_list:
    print("  无数据")
    sys.exit(1)

aweme = aweme_list[0]

# 列出所有顶层字段
print(f"\n[视频] {aweme.get('desc', '')[:80]}")
print(f"\n=== 所有顶层字段 ===")
for k, v in sorted(aweme.items()):
    vt = type(v).__name__
    if isinstance(v, str):
        preview = v[:100] if len(v) > 100 else v
        print(f"  {k}: ({vt}) {preview}")
    elif isinstance(v, (int, float, bool)):
        print(f"  {k}: ({vt}) {v}")
    elif isinstance(v, list):
        print(f"  {k}: ({vt}) [{len(v)} items]")
        if len(v) > 0 and isinstance(v[0], dict):
            print(f"        [0] keys: {list(v[0].keys())[:15]}")
    elif isinstance(v, dict):
        print(f"  {k}: ({vt}) keys={list(v.keys())[:20]}")
    else:
        print(f"  {k}: ({vt}) {v}")

# 搜索所有跟字幕/文本/语言相关的字段
print(f"\n=== 可能含口播/字幕的字段 ===")
keywords = ["subtitle", "caption", "text", "tts", "asr", "speech", "word",
            "sticker", "anchor", "label", "tag", "video_tag", "video_text",
            "interaction", "suggest", "cha_list", "risk", "long_video",
            "ai_tag", "content_desc"]

all_text = json.dumps(aweme, ensure_ascii=False)

for kw in keywords:
    # 找 key 中含有该词的
    for k in aweme:
        if kw.lower() in k.lower():
            val = aweme[k]
            if isinstance(val, str):
                print(f"  [{kw}] {k} = {val[:200]}")
            elif isinstance(val, (list, dict)):
                s = json.dumps(val, ensure_ascii=False)
                print(f"  [{kw}] {k} = {s[:300]}")
            else:
                print(f"  [{kw}] {k} = {val}")

# 检查 video 子字段
video = aweme.get("video", {})
if video:
    print(f"\n=== video 子字段 ===")
    for k, v in sorted(video.items()):
        vt = type(v).__name__
        if isinstance(v, dict):
            print(f"  video.{k}: dict keys={list(v.keys())[:8]}")
        elif isinstance(v, list):
            print(f"  video.{k}: list[{len(v)}]")
            if len(v) > 0 and isinstance(v[0], dict):
                print(f"         [0] keys: {list(v[0].keys())[:10]}")
        elif isinstance(v, str):
            print(f"  video.{k}: str [{len(v)}]={v[:100]}")
        else:
            print(f"  video.{k}: {vt} = {v}")

# 检查音乐/声音相关
music = aweme.get("music", {})
if music:
    print(f"\n=== music 子字段 ===")
    for k, v in music.items():
        vt = type(v).__name__
        if isinstance(v, str):
            print(f"  music.{k}: ({vt}) {v[:150]}")
        elif isinstance(v, (int, float)):
            print(f"  music.{k}: ({vt}) {v}")
        elif isinstance(v, dict):
            print(f"  music.{k}: dict")
        elif isinstance(v, list):
            print(f"  music.{k}: [{len(v)} items]")

# 保存一条完整原始数据
with open("./output/aweme_raw.json", "w", encoding="utf-8") as f:
    json.dump(aweme, f, ensure_ascii=False, indent=2)
print(f"\n[OK] 完整原始数据 -> ./output/aweme_raw.json")
