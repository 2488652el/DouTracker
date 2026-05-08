import json
import os
import re
import sys
import time
from typing import Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from curl_cffi import requests

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
}

PLAIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
}


def extract_sec_uid(url: str) -> Optional[str]:
    match = re.search(r"/user/([A-Za-z0-9_\-]+)", url)
    return match.group(1) if match else None


def resolve_short_url(short_url: str) -> Optional[str]:
    try:
        resp = requests.get(short_url, headers=PLAIN_HEADERS, impersonate="chrome131",
                            allow_redirects=False, timeout=15)
        if resp.status_code in (301, 302):
            return resp.headers.get("Location", "")
    except Exception:
        pass
    return None


def parse_cookies(cookie_str: str) -> dict:
    cookies = {}
    if cookie_str:
        # 过滤占位文字和明显无效的 cookie
        if cookie_str in ("已有Cookie(已隐藏)", "已隐藏", "undefined", "null", ""):
            return {}
        for pair in cookie_str.split(";"):
            pair = pair.strip()
            if "=" in pair:
                k, v = pair.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k and v and k not in ("已有Cookie(已隐藏)", "已隐藏"):
                    cookies[k] = v
    return cookies


def fetch_user_profile(sec_uid: str, cookies: dict = None) -> dict:
    url = "https://www.douyin.com/aweme/v1/web/user/profile/other/"
    params = {
        "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
        "sec_user_id": sec_uid, "version_code": "170400", "version_name": "17.4.0",
        "cookie_enabled": "true", "screen_width": "1920", "screen_height": "1080",
        "browser_language": "zh-CN", "browser_platform": "Win32",
        "browser_name": "Chrome", "browser_version": "131.0.0.0",
        "browser_online": "true", "engine_name": "Blink",
        "engine_version": "131.0.0.0", "os_name": "Windows",
        "os_version": "10", "cpu_core_num": "8",
    }
    try:
        resp = requests.get(url, params=params, headers=API_HEADERS,
                            cookies=cookies, impersonate="chrome131", timeout=20)
        if resp.status_code == 200 and resp.text.strip():
            data = resp.json()
            if data.get("status_code") == 0:
                user = data.get("user", {})
                return {
                    "uid": str(user.get("uid", "")),
                    "sec_uid": user.get("sec_uid", sec_uid),
                    "short_id": user.get("short_id", ""),
                    "nickname": user.get("nickname", ""),
                    "signature": user.get("signature", ""),
                    "avatar_thumb": user.get("avatar_thumb", {}).get("url_list", [""])[0] if user.get("avatar_thumb") else "",
                    "avatar_medium": user.get("avatar_medium", {}).get("url_list", [""])[0] if user.get("avatar_medium") else "",
                    "follower_count": user.get("follower_count", 0),
                    "following_count": user.get("following_count", 0),
                    "total_favorited": user.get("total_favorited", 0),
                    "aweme_count": user.get("aweme_count", 0),
                    "dongtai_count": user.get("dongtai_count", 0),
                    "custom_verify": user.get("custom_verify", ""),
                    "enterprise_verify_reason": user.get("enterprise_verify_reason", ""),
                    "unique_id": user.get("unique_id", ""),
                    "region": user.get("region", ""),
                    "gender": user.get("gender", 0),
                    "birthday": user.get("birthday", ""),
                    "school_name": user.get("school_name", ""),
                    "weibo_verify": user.get("weibo_verify", ""),
                    "commerce_user_level": user.get("commerce_user_level", 0),
                    "verify_info": str(user.get("verify_info", "")),
                    "share_url": f"https://www.douyin.com/user/{sec_uid}",
                }
        return {}
    except Exception as e:
        print(f"[scraper] 获取用户信息失败: {e}")
        return {}


def fetch_user_posts_page(sec_uid: str, max_cursor: int = 0, count: int = 20,
                          cookies: dict = None) -> dict:
    url = "https://www.douyin.com/aweme/v1/web/aweme/post/"
    params = {
        "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
        "sec_user_id": sec_uid, "max_cursor": str(max_cursor), "count": str(count),
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
        resp = requests.get(url, params=params, headers=API_HEADERS,
                            cookies=cookies, impersonate="chrome131", timeout=20)
        if resp.status_code == 200 and resp.text.strip():
            data = resp.json()
            if data.get("status_code") == 0:
                return data
        return {"status_code": -1, "aweme_list": [], "has_more": 0, "max_cursor": 0}
    except Exception as e:
        print(f"[scraper] 获取视频列表失败: {e}")
        return {"status_code": -1, "aweme_list": [], "has_more": 0, "max_cursor": 0}


def extract_video_info(aweme: dict) -> dict:
    video = aweme.get("video", {})
    play_addr = video.get("play_addr", {})
    url_list = play_addr.get("url_list", [])
    play_url = url_list[0] if url_list else ""
    if not play_url:
        bit_rate = video.get("bit_rate", [])
        if bit_rate:
            br_urls = bit_rate[0].get("play_addr", {}).get("url_list", [])
            play_url = br_urls[0] if br_urls else ""

    cover = video.get("cover", {})
    cover_urls = cover.get("url_list", [])
    cover_url = cover_urls[0] if cover_urls else ""

    return {
        "aweme_id": str(aweme.get("aweme_id", "")),
        "desc": aweme.get("desc", ""),
        "create_time": aweme.get("create_time", 0),
        "duration": aweme.get("duration", 0),
        "video_url": play_url,
        "cover_url": cover_url,
        "music_title": aweme.get("music", {}).get("title", ""),
        "music_author": aweme.get("music", {}).get("author", ""),
        "digg_count": aweme.get("statistics", {}).get("digg_count", 0),
        "comment_count": aweme.get("statistics", {}).get("comment_count", 0),
        "share_count": aweme.get("statistics", {}).get("share_count", 0),
        "collect_count": aweme.get("statistics", {}).get("collect_count", 0),
        "play_count": aweme.get("statistics", {}).get("play_count", 0),
        "hashtags": ",".join(
            h.get("title", "") for h in aweme.get("text_extra", []) if h.get("type") == 1
        ),
        "is_top": aweme.get("is_top", 0),
    }


def scrape_blogger(url: str, cookie_str: str = "", max_pages: int = 10,
                   progress_callback=None) -> dict:
    cookies = parse_cookies(cookie_str)

    original_url = url
    if "v.douyin.com" in url:
        resolved = resolve_short_url(url)
        if resolved:
            url = resolved

    sec_uid = extract_sec_uid(url)
    if not sec_uid:
        return {"error": "无法识别的主页链接格式", "videos": []}

    profile = fetch_user_profile(sec_uid, cookies)

    all_videos = []
    max_cursor = 0
    has_more = True
    page = 0

    while has_more and page < max_pages:
        page += 1
        if progress_callback:
            progress_callback(page, max_pages, len(all_videos))

        result = fetch_user_posts_page(sec_uid, max_cursor, count=20, cookies=cookies)
        if result.get("status_code") != 0:
            break

        aweme_list = result.get("aweme_list", [])
        for aweme in aweme_list:
            all_videos.append(extract_video_info(aweme))

        max_cursor = result.get("max_cursor", 0)
        has_more = result.get("has_more", 0) == 1 and len(aweme_list) > 0

        if has_more:
            time.sleep(1)

    return {
        "sec_uid": sec_uid,
        "profile": profile,
        "videos": all_videos,
        "video_count": len(all_videos),
        "shared_url": original_url,
    }
