import json
import time
import os
import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from curl_cffi import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

OUTPUT_DIR = "./output"
SEC_UID = "MS4wLjABAAAA1-M5ZigLVjWEc2LDSKa-4Sm28o0kTSzJOQ0YMbk4EFW_83PMw0dLCKZ2ibLVoOqH"
USER_URL = f"https://www.douyin.com/user/{SEC_UID}"

COOKIES = {
    "ttwid": "7637061083581203978",
    "msToken": "IwiXZtCzySmYrnJUwypAF9cb51rfBwCQ4SbFlE7KBxCwxBc2jfJ7-Ud_L7Z67uENDbYJ0533XwC3I1I2hGKEgu3VUqVIj88mVQ1fWryhq0484Kb622M8UIK5hF1uhf9iPmhtZeh51tmS86nF-F8wbOT_o5P7JZlQPx6EJF1e7PK2cYIwVEBcqg==",
}

session = requests.Session()

print("=" * 60)
print("  抖音视频抓取 (Cookie Session 模式)")
print("=" * 60)

all_videos = []

# Step 1: 先访问首页让 Session 获取额外 cookie
print("\n[Step 1] 访问 douyin.com 首页...")
try:
    r = session.get("https://www.douyin.com/", headers=HEADERS, cookies=COOKIES, impersonate="chrome131", timeout=20)
    print(f"  状态码: {r.status_code}, 长度: {len(r.text)}")
    print(f"  Session cookies: {dict(session.cookies)}")
    if "_$jsvmprt" in r.text:
        print(f"  [!] 仍然是 JS 挑战页")
except Exception as e:
    print(f"  失败: {e}")

# Step 2: 带 Cookie 访问用户主页
print(f"\n[Step 2] 访问用户主页...")
try:
    r = session.get(USER_URL, headers=HEADERS, cookies=COOKIES, impersonate="chrome131", timeout=20)
    print(f"  状态码: {r.status_code}, 长度: {len(r.text)}")
    if "_$jsvmprt" in r.text or r.text.strip().startswith("<html><head><meta"):
        print(f"  [!] JS 挑战页拦截")
    else:
        print(f"  [OK] 正常页面 (前200字): {r.text[:200]}")
except Exception as e:
    print(f"  失败: {e}")

# Step 3: 调用户信息 API
print(f"\n[Step 3] 调用用户信息 API...")
params = {
    "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
    "sec_user_id": SEC_UID, "version_code": "170400", "version_name": "17.4.0",
    "cookie_enabled": "true", "screen_width": "1920", "screen_height": "1080",
    "browser_language": "zh-CN", "browser_platform": "Win32",
    "browser_name": "Chrome", "browser_version": "131.0.0.0",
    "browser_online": "true", "engine_name": "Blink", "engine_version": "131.0.0.0",
    "os_name": "Windows", "os_version": "10", "cpu_core_num": "8",
}
try:
    r = session.get(
        "https://www.douyin.com/aweme/v1/web/user/profile/other/",
        params=params, headers=API_HEADERS, cookies=COOKIES,
        impersonate="chrome131", timeout=20,
    )
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200 and r.text.strip():
        try:
            data = r.json()
            sc = data.get("status_code", -1)
            print(f"  API status_code: {sc}")
            if sc == 0:
                user = data.get("user", {})
                print(f"  [+] 昵称: {user.get('nickname', '?')}")
                print(f"  [+] 粉丝: {user.get('follower_count', 0)}")
                print(f"  [+] 作品数: {user.get('aweme_count', 0)}")
        except Exception:
            print(f"  非JSON响应: {r.text[:200]}")
    else:
        print(f"  空/异常: {r.text[:200]}")
except Exception as e:
    print(f"  请求失败: {e}")

# Step 4: 调视频列表 API
print(f"\n[Step 4] 获取视频列表...")
max_cursor = 0
has_more = True
page = 0

while has_more and page < 10:
    page += 1
    params = {
        "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
        "sec_user_id": SEC_UID, "max_cursor": str(max_cursor), "count": "20",
        "publish_video_strategy_type": "2", "version_code": "170400",
        "version_name": "17.4.0", "cookie_enabled": "true",
        "screen_width": "1920", "screen_height": "1080",
        "browser_language": "zh-CN", "browser_platform": "Win32",
        "browser_name": "Chrome", "browser_version": "131.0.0.0",
        "browser_online": "true", "engine_name": "Blink",
        "engine_version": "131.0.0.0", "os_name": "Windows",
        "os_version": "10", "cpu_core_num": "8",
    }
    try:
        r = session.get(
            "https://www.douyin.com/aweme/v1/web/aweme/post/",
            params=params, headers=API_HEADERS, cookies=COOKIES,
            impersonate="chrome131", timeout=20,
        )
        if r.status_code != 200:
            print(f"  [!] 第{page}页状态码: {r.status_code}")
            print(f"  响应: {r.text[:300]}")
            break

        data = r.json()
        sc = data.get("status_code", -1)
        if sc != 0:
            print(f"  [!] 第{page}页错误: {data.get('status_msg', '')} (code={sc})")
            break

        aweme_list = data.get("aweme_list", [])
        if not aweme_list:
            print(f"  [!] 无数据")
            break

        for a in aweme_list:
            info = {
                "aweme_id": a.get("aweme_id", ""),
                "desc": a.get("desc", ""),
                "create_time": a.get("create_time", 0),
                "duration": a.get("duration", 0),
                "music_title": a.get("music", {}).get("title", ""),
                "statistics": {
                    "digg_count": a.get("statistics", {}).get("digg_count", 0),
                    "comment_count": a.get("statistics", {}).get("comment_count", 0),
                    "share_count": a.get("statistics", {}).get("share_count", 0),
                },
                "hashtags": [
                    h.get("title", "") for h in a.get("text_extra", []) if h.get("type") == 1
                ],
            }
            all_videos.append(info)
            print(f"  [{info['aweme_id']}] {info['desc'][:60]}")

        max_cursor = data.get("max_cursor", 0)
        has_more = data.get("has_more", 0) == 1
        print(f"  第{page}页: {len(aweme_list)}条, 累计{len(all_videos)}条")

        if has_more:
            time.sleep(1.5)
    except Exception as e:
        print(f"  [x] 第{page}页异常: {e}")
        break

# 保存
if all_videos:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, "douyin_videos.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=2)
    txt_path = os.path.join(OUTPUT_DIR, "douyin_captions.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for i, v in enumerate(all_videos, 1):
            f.write(f"{'='*50}\n")
            f.write(f"第{i}条  [{v['aweme_id']}]\n")
            f.write(f"文案: {v['desc']}\n")
            f.write(f"BGM: {v['music_title']}\n")
            f.write(f"点赞:{v['statistics']['digg_count']} 评论:{v['statistics']['comment_count']} 分享:{v['statistics']['share_count']}\n")
            if v["hashtags"]:
                f.write(f"话题: {' #'.join(v['hashtags'])}\n")
            f.write("\n")
    print(f"\n{'='*60}")
    print(f"  [OK] 成功! 共 {len(all_videos)} 条视频")
    print(f"  [OK] {json_path}")
    print(f"  [OK] {txt_path}")
    print(f"{'='*60}")
else:
    print(f"\n{'='*60}")
    print(f"  [!] 云沙箱 + Cookie 仍无法绕过 JS 挑战")
    print(f"{'='*60}")
    print(f"\n  请在本地终端执行浏览器模式 (会自动工作):")
    print(f"  pip install DrissionPage")
    print(f"  python douyin_scraper.py --browser \"{USER_URL}\"")
    print(f"\n  或带 Cookie 的 API 模式 (本地可能有效):")
    print(f'  python douyin_scraper.py --cookie "ttwid=7637061083581203978; msToken=IwiXZtC..." "{USER_URL}"')
