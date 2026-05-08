import re
import json
import time
import os
import sys
import argparse
import csv
from typing import Optional
from urllib.parse import urlparse, parse_qs

# 修复 Windows 控制台 GBK 编码 emoji 报错问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ============================================================
# 抖音主页视频及文案抓取工具
# 支持两种模式:
#   1. API 模式 (默认) - 速度快，但可能需要 cookie
#   2. 浏览器模式 (--browser) - 更稳定，模拟真实浏览器
# ============================================================


def get_requests():
    """尝试导入 curl_cffi (更好的反指纹)，否则回退到 requests"""
    try:
        from curl_cffi import requests as cffi_requests
        return cffi_requests, True
    except ImportError:
        import requests
        return requests, False


# ==================== API 模式 ====================

API_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# 抖音 Web API 端点
USER_INFO_API = "https://www.douyin.com/aweme/v1/web/user/profile/other/"
USER_POST_API = "https://www.douyin.com/aweme/v1/web/aweme/post/"


def extract_sec_uid_from_url(url: str) -> Optional[str]:
    """从抖音主页链接中提取 sec_uid"""
    # 支持格式:
    # https://www.douyin.com/user/MS4wLjABAAAA...
    # https://www.douyin.com/user/xxx?modal_id=...
    # https://v.douyin.com/xxxxx/  (短链，需要重定向)
    pattern = r"/user/([A-Za-z0-9_\-]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def resolve_short_url(short_url: str) -> Optional[str]:
    """解析抖音短链接 (v.douyin.com) 获取真实 URL"""
    requests_mod, is_cffi = get_requests()
    try:
        if is_cffi:
            resp = requests_mod.get(
                short_url,
                headers=API_HEADERS,
                impersonate="chrome131",
                allow_redirects=False,
                timeout=15,
            )
        else:
            resp = requests_mod.get(
                short_url,
                headers=API_HEADERS,
                allow_redirects=False,
                timeout=15,
            )
        if resp.status_code in (301, 302):
            return resp.headers.get("Location", "")
    except Exception as e:
        print(f"  [警告] 短链接解析失败: {e}")
    return None


def fetch_user_info_api(sec_uid: str, cookies: dict = None) -> dict:
    """通过 API 获取用户信息"""
    requests_mod, is_cffi = get_requests()
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "sec_user_id": sec_uid,
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "131.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "131.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "cpu_core_num": "8",
    }
    try:
        if is_cffi:
            resp = requests_mod.get(
                USER_INFO_API,
                params=params,
                headers=API_HEADERS,
                cookies=cookies,
                impersonate="chrome131",
                timeout=15,
            )
        else:
            resp = requests_mod.get(
                USER_INFO_API,
                params=params,
                headers=API_HEADERS,
                cookies=cookies,
                timeout=15,
            )
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"  [错误] 用户信息 API 返回状态码: {resp.status_code}")
            return {}
    except Exception as e:
        print(f"  [错误] 获取用户信息失败: {e}")
        return {}


def fetch_user_posts_api(sec_uid: str, max_cursor: int = 0, count: int = 20, cookies: dict = None) -> dict:
    """通过 API 获取用户视频列表（单页）"""
    requests_mod, is_cffi = get_requests()
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "sec_user_id": sec_uid,
        "max_cursor": str(max_cursor),
        "count": str(count),
        "publish_video_strategy_type": "2",
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "131.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "131.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "cpu_core_num": "8",
    }
    try:
        if is_cffi:
            resp = requests_mod.get(
                USER_POST_API,
                params=params,
                headers=API_HEADERS,
                cookies=cookies,
                impersonate="chrome131",
                timeout=15,
            )
        else:
            resp = requests_mod.get(
                USER_POST_API,
                params=params,
                headers=API_HEADERS,
                cookies=cookies,
                timeout=15,
            )
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"  [错误] 视频列表 API 返回状态码: {resp.status_code}")
            return {}
    except Exception as e:
        print(f"  [错误] 获取视频列表失败: {e}")
        return {}


def extract_video_info(aweme: dict) -> dict:
    """从 aweme 数据中提取视频信息（含文案）"""
    return {
        "aweme_id": aweme.get("aweme_id", ""),
        "desc": aweme.get("desc", ""),  # 文案 / 描述
        "create_time": aweme.get("create_time", 0),
        "duration": aweme.get("duration", 0),
        "video_play_url": _extract_play_url(aweme),
        "cover_url": _extract_cover_url(aweme),
        "music_title": aweme.get("music", {}).get("title", ""),
        "music_author": aweme.get("music", {}).get("author", ""),
        "statistics": {
            "digg_count": aweme.get("statistics", {}).get("digg_count", 0),
            "comment_count": aweme.get("statistics", {}).get("comment_count", 0),
            "share_count": aweme.get("statistics", {}).get("share_count", 0),
            "play_count": aweme.get("statistics", {}).get("play_count", 0),
        },
        "hashtags": [
            h.get("title", "")
            for h in aweme.get("text_extra", [])
            if h.get("type") == 1
        ],
        "is_top": aweme.get("is_top", 0),  # 是否置顶
    }


def _extract_play_url(aweme: dict) -> str:
    """提取无水印播放地址"""
    video = aweme.get("video", {})
    play_addr = video.get("play_addr", {})
    url_list = play_addr.get("url_list", [])
    if url_list:
        return url_list[0]
    # 备用: bit_rate 列表中的高清地址
    bit_rate = video.get("bit_rate", [])
    if bit_rate:
        play_addr_br = bit_rate[0].get("play_addr", {})
        url_list_br = play_addr_br.get("url_list", [])
        if url_list_br:
            return url_list_br[0]
    return ""


def _extract_cover_url(aweme: dict) -> str:
    """提取封面图地址"""
    cover = aweme.get("video", {}).get("cover", {})
    url_list = cover.get("url_list", [])
    if url_list:
        return url_list[0]
    return ""


def scrape_by_api(url: str, max_pages: int = 10, cookies_str: str = "") -> list:
    """使用 API 模式抓取抖音用户主页视频"""
    print("\n" + "=" * 60)
    print("  🔧 使用 API 模式抓取")
    print("=" * 60)

    # 1. 处理短链接
    original_url = url
    if "v.douyin.com" in url:
        print(f"  [1] 解析短链接: {url}")
        resolved = resolve_short_url(url)
        if resolved:
            url = resolved
            print(f"  [√] 解析结果: {url}")
        else:
            print("  [×] 短链接解析失败，尝试直接用原链接...")

    # 2. 提取 sec_uid
    sec_uid = extract_sec_uid_from_url(url)
    if not sec_uid:
        print(f"  [×] 无法从链接中提取用户 ID: {url}")
        print(f"  请确认链接格式: https://www.douyin.com/user/MS4wLjABAAAA...")
        return []

    print(f"  [2] 用户 sec_uid: {sec_uid}")

    # 3. 解析 cookies
    cookies = {}
    if cookies_str:
        for pair in cookies_str.split(";"):
            pair = pair.strip()
            if "=" in pair:
                k, v = pair.split("=", 1)
                cookies[k.strip()] = v.strip()

    # 4. 获取用户信息
    print(f"  [3] 获取用户基本信息...")
    user_info = fetch_user_info_api(sec_uid, cookies)
    if user_info.get("status_code") == 0:
        user_data = user_info.get("user", {})
        print(f"  [√] 昵称: {user_data.get('nickname', '未知')}")
        print(f"  [√] 粉丝: {user_data.get('follower_count', 0)}")
        print(f"  [√] 获赞: {user_data.get('total_favorited', 0)}")
        print(f"  [√] 作品数: {user_data.get('aweme_count', 0)}")
    else:
        print(f"  [!] 获取用户信息失败，继续尝试获取视频...")

    # 5. 分页获取视频
    all_videos = []
    max_cursor = 0
    has_more = True
    page = 0

    while has_more and page < max_pages:
        page += 1
        print(f"  [4] 获取第 {page} 页视频...")
        result = fetch_user_posts_api(sec_uid, max_cursor, count=20, cookies=cookies)

        if not result:
            print(f"  [!] 第 {page} 页获取失败，停止")
            break

        aweme_list = result.get("aweme_list", [])
        if not aweme_list:
            print(f"  [!] 没有更多视频")
            break

        for aweme in aweme_list:
            video_info = extract_video_info(aweme)
            all_videos.append(video_info)
            desc_preview = video_info["desc"][:50] if video_info["desc"] else "(无文案)"
            print(f"    - [{video_info['aweme_id']}] {desc_preview}")

        max_cursor = result.get("max_cursor", 0)
        has_more = result.get("has_more", 0) == 1
        print(f"  [√] 第 {page} 页: 获取 {len(aweme_list)} 条，累计 {len(all_videos)} 条")

        if has_more:
            time.sleep(1.5)  # 避免请求过快

    print(f"\n  [完成] 共获取 {len(all_videos)} 条视频")
    return all_videos


# ==================== 浏览器模式 (DrissionPage) ====================

def _find_browser_path() -> str:
    """自动查找系统可用的浏览器路径"""
    paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return ""


def scrape_by_browser(url: str, max_scroll: int = 50) -> list:
    """使用 DrissionPage 浏览器模式 + API 拦截抓取"""
    print("\n" + "=" * 60)
    print("  浏览器模式抓取 (DrissionPage + API 拦截)")
    print("=" * 60)

    try:
        from DrissionPage import ChromiumPage, ChromiumOptions
    except ImportError:
        print("  [x] 请先安装: pip install DrissionPage")
        return []

    browser_path = _find_browser_path()
    print(f"  [1] 浏览器路径: {browser_path or '自动检测'}")

    co = ChromiumOptions()
    if browser_path:
        co.set_browser_path(browser_path)
    co.set_argument("--disable-blink-features=AutomationControlled")
    co.set_argument("--disable-infobars")
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-gpu")
    co.set_argument("--disable-dev-shm-usage")
    co.headless(False)

    try:
        page = ChromiumPage(co)
    except Exception as e:
        print(f"  [x] 浏览器启动失败: {e}")
        return []

    print(f"  [OK] 浏览器已启动")

    # 监听抖音 API 响应
    page.listen.start("aweme/v1/web/aweme/post/")
    page.listen.start("aweme/v1/web/user/profile/other/")

    print(f"  [2] 打开页面: {url}")
    try:
        page.get(url, timeout=60)
    except Exception as e:
        print(f"  [x] 页面加载失败: {e}")
        page.quit()
        return []

    print(f"  [OK] 页面已加载")
    time.sleep(5)

    # 提取 API 拦截数据
    all_videos = []
    seen_ids = set()

    print(f"  [3] 提取数据...")
    packets = list(page.listen.steps())
    print(f"  捕获 {len(packets)} 个网络包")

    for pkt in packets:
        try:
            body = pkt.response.body
            if not body:
                continue
            data = json.loads(body)

            user = data.get("user", {})
            if user:
                print(f"  [用户] {user.get('nickname', '?')} | 粉丝:{user.get('follower_count',0)} | 作品:{user.get('aweme_count',0)}")

            for aweme in data.get("aweme_list", []):
                info = extract_video_info(aweme)
                aid = info["aweme_id"]
                if aid and aid not in seen_ids:
                    seen_ids.add(aid)
                    all_videos.append(info)
                    desc_preview = info["desc"][:60] if info["desc"] else "(无文案)"
                    print(f"  [{aid}] {desc_preview}")
        except Exception:
            pass

    # 滚动加载更多
    if all_videos:
        print(f"\n  [4] 滚动加载更多...")
        scroll_count = 0
        last_count = len(all_videos)
        no_new = 0

        while scroll_count < max_scroll and no_new < 8:
            scroll_count += 1
            page.listen.start("aweme/v1/web/aweme/post/")
            page.scroll.down(500)
            time.sleep(2)

            for pkt in list(page.listen.steps()):
                try:
                    body = pkt.response.body
                    if not body:
                        continue
                    data = json.loads(body)
                    for aweme in data.get("aweme_list", []):
                        info = extract_video_info(aweme)
                        aid = info["aweme_id"]
                        if aid and aid not in seen_ids:
                            seen_ids.add(aid)
                            all_videos.append(info)
                            desc_preview = info["desc"][:60] if info["desc"] else "(无文案)"
                            print(f"  [{aid}] {desc_preview}")
                except Exception:
                    pass

            cur = len(all_videos)
            if cur == last_count:
                no_new += 1
            else:
                no_new = 0
            last_count = cur
            print(f"    滚动 {scroll_count}/{max_scroll} | 累计 {cur} 条", end="\r")

    print()
    page.quit()
    print(f"  [完成] 共获取 {len(all_videos)} 条视频")
    return all_videos


# ==================== 备选浏览器模式 (Playwright) ====================

def scrape_by_playwright(url: str, max_scroll: int = 50) -> list:
    """使用 Playwright 浏览器抓取（需要手动扫码登录）"""
    print("\n" + "=" * 60)
    print("  🌐 使用浏览器模式抓取 (Playwright)")
    print("=" * 60)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [×] 请先安装 Playwright: pip install playwright && playwright install chromium")
        return []

    all_videos = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        # 注入反检测脚本
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

        print(f"  [1] 打开页面: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        print(f"  [2] 等待页面渲染...")
        time.sleep(3)

        # 尝试从页面提取初始数据
        try:
            page_html = page.content()
            pattern = r'__UNIVERSAL_DATA__\s*=\s*({.*?})\s*</script>'
            match = re.search(pattern, page_html, re.DOTALL)
            if match:
                raw_data = json.loads(match.group(1))
                user_data = raw_data.get("__DEFAULT_SLUG__", {}).get("userInfo", {})
                print(f"  [√] 用户: {user_data.get('nickname', {})}")

                post_data = raw_data.get("__DEFAULT_SLUG__", {}).get("post", {})
                if isinstance(post_data, dict):
                    aweme_list = post_data.get("list", [])
                    if not aweme_list:
                        aweme_list = post_data.get("data", [])
                    for aweme in aweme_list:
                        if isinstance(aweme, dict):
                            info = {
                                "aweme_id": aweme.get("aweme_id", ""),
                                "desc": aweme.get("desc", ""),
                                "create_time": aweme.get("create_time", 0),
                                "source": "universal_data",
                            }
                            all_videos.append(info)
                            desc_preview = info["desc"][:50] if info["desc"] else "(无文案)"
                            print(f"    - [{info['aweme_id']}] {desc_preview}")
        except Exception as e:
            print(f"  [!] 初始数据提取异常: {e}")

        # 滚动加载更多
        scroll_count = 0
        last_count = len(all_videos)
        no_new_count = 0

        print(f"  [3] 滚动加载更多视频...")
        while scroll_count < max_scroll and no_new_count < 5:
            scroll_count += 1
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(2)

            # 捕获 API 响应
            try:
                page_html = page.content()
                # 尝试匹配 aweme 数据
                pattern = r'"aweme_id":"(\d+)".*?"desc":"([^"]*)"'
                matches = re.findall(pattern, page_html)
                for aweme_id, desc in matches:
                    if aweme_id not in {v.get("aweme_id") for v in all_videos if v.get("aweme_id")}:
                        all_videos.append({
                            "aweme_id": aweme_id,
                            "desc": desc,
                            "source": "dom_regex",
                        })
                        desc_preview = desc[:50] if desc else "(无文案)"
                        print(f"    - [{aweme_id}] {desc_preview}")
            except Exception:
                pass

            new_count = len(all_videos)
            if new_count == last_count:
                no_new_count += 1
            else:
                no_new_count = 0
            last_count = new_count

            print(f"    滚动 {scroll_count}/{max_scroll} | 已提取 {new_count} 条" + " " * 10, end="\r")

        browser.close()

    print(f"\n  [完成] Playwright 模式共获取 {len(all_videos)} 条视频")
    return all_videos


# ==================== 保存结果 ====================

def save_results(videos: list, output_dir: str = "./output", author_name: str = ""):
    """保存抓取结果到 JSON 和 CSV 文件"""
    if not videos:
        print("\n  [!] 没有数据可保存")
        return

    os.makedirs(output_dir, exist_ok=True)

    # JSON 格式（完整数据）
    json_path = os.path.join(output_dir, f"{author_name or 'douyin'}_videos.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"\n  [√] JSON 已保存: {json_path}")

    # CSV 格式（核心字段）
    csv_path = os.path.join(output_dir, f"{author_name or 'douyin'}_captions.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        # 写表头
        if videos and isinstance(videos[0], dict):
            headers = list(videos[0].keys())
            writer.writerow(headers)
            for v in videos:
                writer.writerow([v.get(h, "") for h in headers])
        else:
            writer.writerow(["desc"])
            for v in videos:
                writer.writerow([v.get("desc", "")])

    print(f"  [√] CSV 已保存: {csv_path}")

    # 纯文本文案（方便阅读）
    txt_path = os.path.join(output_dir, f"{author_name or 'douyin'}_captions.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for i, v in enumerate(videos, 1):
            desc = v.get("desc", "")
            aweme_id = v.get("aweme_id", "")
            if desc:
                f.write(f"{i}. [{aweme_id}] {desc}\n")

    print(f"  [√] 纯文本文案已保存: {txt_path}")


# ==================== 主入口 ====================

def main():
    parser = argparse.ArgumentParser(
        description="抖音主页视频及文案抓取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # API 模式 (默认)
  python douyin_scraper.py "https://www.douyin.com/user/MS4wLjABAAAA..."

  # 浏览器模式 (需要安装 DrissionPage)
  python douyin_scraper.py "https://www.douyin.com/user/xxx" --browser

  # Playwright 模式
  python douyin_scraper.py "https://www.douyin.com/user/xxx" --playwright

  # 带 Cookie
  python douyin_scraper.py "https://www.douyin.com/user/xxx" --cookie "ttwid=xxx; msToken=xxx"

  # 限制抓取页数
  python douyin_scraper.py "https://www.douyin.com/user/xxx" --max-pages 5

  # 指定输出目录
  python douyin_scraper.py "https://www.douyin.com/user/xxx" --output ./my_videos
        """,
    )
    parser.add_argument("url", help="抖音用户主页链接")
    parser.add_argument("--browser", action="store_true", help="使用浏览器模式 (DrissionPage)")
    parser.add_argument("--playwright", action="store_true", help="使用 Playwright 浏览器模式")
    parser.add_argument("--cookie", type=str, default="", help="Cookie 字符串 (格式: key1=value1; key2=value2)")
    parser.add_argument("--max-pages", type=int, default=10, help="最大抓取页数/滚动次数 (默认: 10)")
    parser.add_argument("--output", type=str, default="./output", help="输出目录 (默认: ./output)")

    args = parser.parse_args()

    print("\n" + "█" * 60)
    print("  抖音主页视频及文案抓取工具")
    print("█" * 60)

    videos = []

    if args.playwright:
        videos = scrape_by_playwright(args.url, max_scroll=args.max_pages)
    elif args.browser:
        videos = scrape_by_browser(args.url, max_scroll=args.max_pages)
    else:
        videos = scrape_by_api(args.url, max_pages=args.max_pages, cookies_str=args.cookie)

    if videos:
        # 确定作者名称
        author_name = ""
        save_results(videos, args.output, author_name)
        print("\n" + "=" * 60)
        print(f"  🎉 抓取完成！共获取 {len(videos)} 条视频/文案")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  ⚠️ 未获取到任何数据")
        print("=" * 60)
        print("  可能的原因:")
        print("  1. 抖音反爬机制 - 请尝试添加 Cookie (--cookie)")
        print("  2. 用户 ID 格式不正确")
        print("  3. 网络问题")
        print("  4. 该用户未发布任何视频")
        print()
        print("  建议:")
        print("  1. 使用浏览器模式: --browser 或 --playwright")
        print("  2. 从浏览器中复制 Cookie 使用: --cookie")
        print("  3. 如何获取 Cookie:")
        print("     a. 打开浏览器并登录抖音网页版")
        print("     b. F12 → Application → Cookies → douyin.com")
        print("     c. 复制 ttwid 和 msToken 的值")
        print("     d. 格式: --cookie \"ttwid=xxx; msToken=xxx\"")


if __name__ == "__main__":
    main()
