import sqlite3
import json
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "douyin_app.db")


def _get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    db = _get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS bloggers (
            sec_uid TEXT PRIMARY KEY,
            nickname TEXT,
            uid TEXT,
            signature TEXT,
            avatar_thumb TEXT,
            avatar_medium TEXT,
            follower_count INTEGER DEFAULT 0,
            following_count INTEGER DEFAULT 0,
            total_favorited INTEGER DEFAULT 0,
            aweme_count INTEGER DEFAULT 0,
            dongtai_count INTEGER DEFAULT 0,
            custom_verify TEXT,
            enterprise_verify_reason TEXT,
            gender INTEGER DEFAULT 0,
            region TEXT,
            share_url TEXT,
            unique_id TEXT,
            extra_json TEXT,
            created_at REAL,
            updated_at REAL
        );

        CREATE TABLE IF NOT EXISTS videos (
            aweme_id TEXT PRIMARY KEY,
            blogger_sec_uid TEXT,
            `desc` TEXT,
            create_time INTEGER,
            duration INTEGER,
            video_url TEXT,
            cover_url TEXT,
            music_title TEXT,
            music_author TEXT,
            digg_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            share_count INTEGER DEFAULT 0,
            collect_count INTEGER DEFAULT 0,
            play_count INTEGER DEFAULT 0,
            hashtags TEXT,
            is_top INTEGER DEFAULT 0,
            fetched_at REAL,
            FOREIGN KEY (blogger_sec_uid) REFERENCES bloggers(sec_uid) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_videos_blogger ON videos(blogger_sec_uid);
        CREATE INDEX IF NOT EXISTS idx_videos_create_time ON videos(create_time DESC);
    """)
    db.commit()
    db.close()


def save_settings(cookie_str: str = "", max_pages: int = 10):
    db = _get_db()
    now = time.time()
    db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("cookie", cookie_str))
    db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("max_pages", str(max_pages)))
    db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("last_save", str(now)))
    db.commit()
    db.close()


def get_settings() -> dict:
    db = _get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    db.close()
    return {r["key"]: r["value"] for r in rows}


def save_blogger(profile: dict, sec_uid: str, share_url: str):
    db = _get_db()
    now = time.time()
    db.execute("""
        INSERT OR REPLACE INTO bloggers
        (sec_uid, nickname, uid, signature, avatar_thumb, avatar_medium,
         follower_count, following_count, total_favorited, aweme_count,
         dongtai_count, custom_verify, enterprise_verify_reason,
         gender, region, share_url, unique_id, extra_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sec_uid, profile.get("nickname", ""), profile.get("uid", ""),
        profile.get("signature", ""), profile.get("avatar_thumb", ""),
        profile.get("avatar_medium", ""),
        profile.get("follower_count", 0), profile.get("following_count", 0),
        profile.get("total_favorited", 0), profile.get("aweme_count", 0),
        profile.get("dongtai_count", 0),
        profile.get("custom_verify", ""), profile.get("enterprise_verify_reason", ""),
        profile.get("gender", 0), profile.get("region", ""),
        share_url, profile.get("unique_id", ""), json.dumps(profile, ensure_ascii=False),
        now, now,
    ))
    db.commit()
    db.close()


def save_videos(videos: list, sec_uid: str):
    db = _get_db()
    now = time.time()
    for v in videos:
        db.execute("""
            INSERT OR REPLACE INTO videos
            (aweme_id, blogger_sec_uid, `desc`, create_time, duration,
             video_url, cover_url, music_title, music_author,
             digg_count, comment_count, share_count, collect_count, play_count,
             hashtags, is_top, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            v["aweme_id"], sec_uid, v["desc"], v["create_time"], v["duration"],
            v["video_url"], v["cover_url"], v["music_title"], v["music_author"],
            v["digg_count"], v["comment_count"], v["share_count"],
            v["collect_count"], v["play_count"],
            v["hashtags"], v.get("is_top", 0), now,
        ))
    db.commit()
    db.close()


def get_all_bloggers() -> list:
    db = _get_db()
    rows = db.execute("""
        SELECT sec_uid, nickname, uid, signature, avatar_thumb, avatar_medium,
               follower_count, following_count, total_favorited, aweme_count,
               dongtai_count, custom_verify, gender, region, share_url,
               unique_id, created_at, updated_at,
               (SELECT COUNT(*) FROM videos WHERE blogger_sec_uid = bloggers.sec_uid) as local_video_count
        FROM bloggers ORDER BY updated_at DESC
    """).fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_blogger_detail(sec_uid: str) -> dict:
    db = _get_db()
    blogger = db.execute("SELECT * FROM bloggers WHERE sec_uid = ?", (sec_uid,)).fetchone()
    if not blogger:
        db.close()
        return None
    videos = db.execute(
        "SELECT * FROM videos WHERE blogger_sec_uid = ? ORDER BY create_time DESC",
        (sec_uid,)
    ).fetchall()
    db.close()
    return {
        "blogger": dict(blogger),
        "videos": [dict(v) for v in videos],
    }


def get_blogger_videos(sec_uid: str, sort_by: str = "create_time",
                       order: str = "DESC", limit: int = 500, offset: int = 0) -> dict:
    db = _get_db()
    allowed_sorts = ["create_time", "digg_count", "comment_count", "share_count",
                     "collect_count", "play_count", "duration"]
    if sort_by not in allowed_sorts:
        sort_by = "create_time"
    if order.upper() not in ("ASC", "DESC"):
        order = "DESC"

    total = db.execute(
        "SELECT COUNT(*) FROM videos WHERE blogger_sec_uid = ?", (sec_uid,)
    ).fetchone()[0]

    rows = db.execute(
        f"SELECT * FROM videos WHERE blogger_sec_uid = ? ORDER BY {sort_by} {order} LIMIT ? OFFSET ?",
        (sec_uid, limit, offset)
    ).fetchall()
    db.close()
    return {
        "videos": [dict(r) for r in rows],
        "total": total,
        "sort_by": sort_by,
        "order": order,
    }


def delete_blogger(sec_uid: str):
    db = _get_db()
    db.execute("DELETE FROM videos WHERE blogger_sec_uid = ?", (sec_uid,))
    db.execute("DELETE FROM bloggers WHERE sec_uid = ?", (sec_uid,))
    db.commit()
    db.close()


def get_blogger_stats_summary(sec_uid: str = None) -> dict:
    db = _get_db()
    if sec_uid:
        rows = db.execute("""
            SELECT SUM(digg_count) as total_likes, SUM(comment_count) as total_comments,
                   SUM(share_count) as total_shares, SUM(collect_count) as total_collects,
                   SUM(play_count) as total_plays, COUNT(*) as video_count,
                   AVG(digg_count) as avg_likes, AVG(comment_count) as avg_comments,
                   AVG(share_count) as avg_shares
            FROM videos WHERE blogger_sec_uid = ?
        """, (sec_uid,)).fetchone()
    else:
        rows = db.execute("""
            SELECT SUM(digg_count) as total_likes, SUM(comment_count) as total_comments,
                   SUM(share_count) as total_shares, SUM(collect_count) as total_collects,
                   SUM(play_count) as total_plays, COUNT(*) as video_count,
                   AVG(digg_count) as avg_likes, AVG(comment_count) as avg_comments,
                   AVG(share_count) as avg_shares
            FROM videos
        """).fetchone()
    db.close()
    return dict(rows) if rows else {}
