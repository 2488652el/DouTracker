import os
import sys
import socket
import webbrowser
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import router as api_router
from backend.database import init_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        for i in range(2, 255):
            try:
                import subprocess
                out = subprocess.check_output("ipconfig", shell=True, encoding="gbk", errors="ignore")
                for line in out.splitlines():
                    if "IPv4" in line:
                        parts = line.strip().split(":")
                        if len(parts) == 2:
                            return parts[-1].strip()
            except Exception:
                pass
            time.sleep(0.01)
    return "无法获取"

app = FastAPI(title="DouTracker - 抖音博主数据面板", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(api_router)

static_dirs = [
    ("/assets", os.path.join(BASE_DIR, "assets")),
    ("/", os.path.join(BASE_DIR, "frontend")),
]
for path, directory in static_dirs:
    if os.path.isdir(directory):
        app.mount(path, StaticFiles(directory=directory, html=True), name=path.strip("/") or "root")


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8899")


if __name__ == "__main__":
    import uvicorn

    lan_ip = _get_lan_ip()

    print("\n" + "=" * 55)
    print("  \U0001f4ca DouTracker - 抖音博主数据面板 v2.0")
    print(f"  本机访问:   http://127.0.0.1:8899")
    print(f"  局域网访问: http://{lan_ip}:8899")
    print("  API 端点:   http://127.0.0.1:8899/api")
    print("  PWA 安装:   浏览器地址栏右侧 \u2795 安装图标")
    print("-" * 55)
    print("  提示: 其他设备访问时, 请确保防火墙允许 8899 端口")
    print("=" * 55 + "\n")

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(app, host="0.0.0.0", port=8899, log_level="warning")
