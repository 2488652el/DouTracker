import json
import threading
import time
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os

from . import scraper, database

router = APIRouter(prefix="/api")

database.init_db()

_progress = {"status": "idle", "page": 0, "total_pages": 0, "video_count": 0,
             "message": "", "sec_uid": ""}


class ScrapeRequest(BaseModel):
    url: str
    cookie: str = ""
    max_pages: int = 10


class SettingsUpdate(BaseModel):
    cookie: str = ""
    max_pages: int = 10


@router.get("/settings")
def get_settings():
    s = database.get_settings()
    cookie = s.get("cookie", "")
    safe = cookie[:30] + "..." if len(cookie) > 30 else cookie
    return {
        "cookie_masked": safe,
        "cookie_exists": bool(cookie),
        "max_pages": int(s.get("max_pages", "10")),
        "last_save": s.get("last_save", ""),
        "autostart": _check_autostart(),
    }


@router.post("/settings")
def update_settings(data: SettingsUpdate):
    cookie = data.cookie
    if cookie in ("已有Cookie(已隐藏)", "已隐藏", "undefined", "null"):
        cookie = ""
    database.save_settings(cookie, data.max_pages)
    return {"ok": True, "cookie_saved": bool(cookie)}


# ====== Autostart ======

def _autostart_link_path() -> str:
    startup_dir = os.path.join(os.environ.get("APPDATA", ""),
                               r"Microsoft\Windows\Start Menu\Programs\Startup")
    return os.path.join(startup_dir, "DouTracker.lnk")


def _autostart_bat_path() -> str:
    startup_dir = os.path.join(os.environ.get("APPDATA", ""),
                               r"Microsoft\Windows\Start Menu\Programs\Startup")
    return os.path.join(startup_dir, "DouTracker.bat")


def _check_autostart() -> bool:
    """检查开机自启状态: 优先读取数据库持久化记录, 同时验证文件系统"""
    s = database.get_settings()
    db_val = s.get("autostart", "")
    if db_val == "1":
        return True
    if db_val == "0":
        return False
    return os.path.exists(_autostart_link_path()) or os.path.exists(_autostart_bat_path())


def _save_autostart_pref(enabled: bool):
    """持久化开机自启偏好到数据库"""
    db = database._get_db()
    db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
               ("autostart", "1" if enabled else "0"))
    db.commit()
    db.close()


def _apply_filesystem(enabled: bool):
    """尝试在 Windows 启动文件夹创建/删除快捷方式 (best-effort)"""
    import shutil
    link = _autostart_link_path()
    bat_dest = _autostart_bat_path()

    if not enabled:
        for p in [link, bat_dest]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
        return

    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    bat_src = os.path.join(app_dir, "launch_doutracker.bat")
    if os.path.exists(bat_src):
        try:
            shutil.copy2(bat_src, bat_dest)
        except Exception:
            pass

    vbs_path = os.path.join(app_dir, "launch_doutracker.vbs")
    icon_path = os.path.join(app_dir, "assets", "favicon.ico")
    try:
        import subprocess
        script = (
            f'$s=(New-Object -ComObject WScript.Shell).CreateShortcut("{link}");'
            f'$s.TargetPath="wscript.exe";$s.Arguments=\'{vbs_path}\';'
            f'$s.WorkingDirectory="{app_dir}";$s.WindowStyle=7;'
            f'$s.IconLocation="{icon_path}";'
            f'$s.Description="DouTracker";$s.Save()'
        )
        subprocess.run(["powershell", "-Command", script], capture_output=True)
    except Exception:
        pass


@router.post("/autostart/toggle")
def toggle_autostart():
    current = _check_autostart()
    enabled = not current
    _save_autostart_pref(enabled)
    _apply_filesystem(enabled)
    return {"autostart": enabled, "message": "已启用开机自启" if enabled else "已禁用开机自启"}


@router.get("/autostart")
def get_autostart():
    return {"autostart": _check_autostart()}


@router.post("/scrape")
def scrape(data: ScrapeRequest):
    global _progress
    if _progress["status"] == "running":
        raise HTTPException(400, "已有抓取任务在运行")

    _progress = {"status": "running", "page": 0, "total_pages": data.max_pages,
                 "video_count": 0, "message": "正在抓取...", "sec_uid": ""}

    def _run():
        global _progress
        try:
            cookie = data.cookie or database.get_settings().get("cookie", "")

            def progress_cb(page, total, vcount):
                _progress["page"] = page
                _progress["video_count"] = vcount
                _progress["message"] = f"第{page}/{total}页, 已获取{vcount}条"

            result = scraper.scrape_blogger(data.url, cookie, data.max_pages, progress_cb)

            if "error" in result:
                _progress["status"] = "error"
                _progress["message"] = result["error"]
                return

            profile = result.get("profile", {})
            sec_uid = result.get("sec_uid", "")
            videos = result.get("videos", [])
            _progress["sec_uid"] = sec_uid

            if profile:
                database.save_blogger(profile, sec_uid, result.get("shared_url", ""))
            if videos:
                database.save_videos(videos, sec_uid)

            _progress["status"] = "done"
            _progress["message"] = f"完成! 博主: {profile.get('nickname','?')}, 视频: {len(videos)}条"
        except Exception as e:
            _progress["status"] = "error"
            _progress["message"] = str(e)

    threading.Thread(target=_run, daemon=True).start()
    return {"ok": True, "message": "抓取开始"}


@router.get("/progress")
def get_progress():
    return _progress


@router.get("/bloggers")
def list_bloggers():
    bloggers = database.get_all_bloggers()
    return {"bloggers": bloggers, "total": len(bloggers)}


@router.get("/bloggers/{sec_uid}")
def blogger_detail(sec_uid: str):
    detail = database.get_blogger_detail(sec_uid)
    if not detail:
        raise HTTPException(404, "博主不存在")
    return detail


@router.get("/bloggers/{sec_uid}/videos")
def blogger_videos(
    sec_uid: str, sort_by: str = Query("create_time"),
    order: str = Query("DESC"), limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    return database.get_blogger_videos(sec_uid, sort_by, order, limit, offset)


@router.get("/bloggers/{sec_uid}/stats")
def blogger_stats(sec_uid: str):
    stats = database.get_blogger_stats_summary(sec_uid)
    blogger = database.get_blogger_detail(sec_uid)
    profile = blogger["blogger"] if blogger else {}
    return {
        "profile": {
            "nickname": profile.get("nickname", ""),
            "follower_count": profile.get("follower_count", 0),
            "aweme_count": profile.get("aweme_count", 0),
            "total_favorited": profile.get("total_favorited", 0),
        },
        "stats": stats,
    }


@router.delete("/bloggers/{sec_uid}")
def remove_blogger(sec_uid: str):
    database.delete_blogger(sec_uid)
    return {"ok": True}


@router.get("/export/{sec_uid}")
def export_data(sec_uid: str, fmt: str = Query("json")):
    detail = database.get_blogger_detail(sec_uid)
    if not detail:
        raise HTTPException(404, "博主不存在")

    videos = detail["videos"]
    blogger = detail["blogger"]

    if fmt == "csv":
        import io, csv as csv_mod
        output = io.StringIO()
        writer = csv_mod.writer(output)
        writer.writerow(["aweme_id", "desc", "create_time", "digg_count",
                         "comment_count", "share_count", "collect_count",
                         "play_count", "duration", "music_title", "hashtags"])
        for v in videos:
            writer.writerow([v["aweme_id"], v["desc"], v["create_time"],
                            v["digg_count"], v["comment_count"], v["share_count"],
                            v["collect_count"], v["play_count"], v["duration"],
                            v["music_title"], v["hashtags"]])
        return PlainTextResponse(output.getvalue(), media_type="text/csv",
                                 headers={"Content-Disposition": f"attachment; filename={sec_uid}.csv"})

    return {
        "blogger": {k: v for k, v in dict(blogger).items() if not k.startswith("extra_")},
        "videos": videos,
        "exported_at": time.time(),
    }


@router.get("/dashboard")
def dashboard_stats():
    bloggers = database.get_all_bloggers()
    all_stats = database.get_blogger_stats_summary()

    total_videos = sum(b["local_video_count"] for b in bloggers)
    total_followers = sum(b["follower_count"] for b in bloggers)
    total_likes = all_stats.get("total_likes", 0) or 0

    return {
        "blogger_count": len(bloggers),
        "total_videos": total_videos,
        "total_followers": total_followers,
        "total_likes": total_likes,
        "total_comments": all_stats.get("total_comments", 0) or 0,
        "total_shares": all_stats.get("total_shares", 0) or 0,
        "avg_likes": round(all_stats.get("avg_likes", 0) or 0, 1),
        "avg_comments": round(all_stats.get("avg_comments", 0) or 0, 1),
        "bloggers": bloggers,
    }
