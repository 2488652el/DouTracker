# 📊 DouTracker — 抖音博主数据面板

多博主管理 · 视频数据分析 · 可视化仪表盘 · 局域网共享 · 开机自启

---

## ✨ 功能

| 模块 | 说明 |
|------|------|
| 📥 **多博主抓取** | 输入抖音主页链接，自动获取博主 UID、粉丝数、获赞数、简介等全部公开数据 |
| 📹 **视频全量采集** | 分页抓取所有视频，含文案、播放链接、封面、BGM、话题标签 |
| 📊 **数据仪表盘** | 粉丝/获赞/作品数统计卡片、Top 10 点赞横向柱状图、完整视频表格 |
| 🔍 **排序与搜索** | 视频表可按照点赞/评论/分享/收藏/发布时间多列排序，支持文案关键词搜索 |
| 📤 **一键导出** | JSON / CSV 格式导出 |
| 🎨 **模块化布局** | 拖拽重排卡片模块（Profile / Stats / Charts / Videos） |
| 🔌 **开机自启** | 设置面板滑动开关，数据库持久化 |
| 🌐 **局域网共享** | `host="0.0.0.0"`，同一网络下其他设备可访问 |
| 🔼 **返回顶部** | 滚动 > 400px 自动显示，平滑动画 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动

```bash
python app.py
```

浏览器自动打开 `http://127.0.0.1:8899`

### 3. 配置 Cookie（重要）

抖音 API 需要登录态 Cookie 才能拉取数据：

1. 浏览器打开 [douyin.com](https://www.douyin.com) 并登录
2. F12 → Application → Cookies → `douyin.com`
3. 复制所有 cookie 粘贴到面板设置页

---

## 📁 项目结构

```
├── app.py                    # 主入口（FastAPI + Uvicorn）
├── backend/
│   ├── scraper.py            # 抖音数据抓取（curl_cffi，TLS 指纹伪装）
│   ├── database.py           # SQLite 持久化层（博主 + 视频 + 设置）
│   └── api.py                # REST API（14 个端点）
├── frontend/
│   ├── index.html            # 完整 SPA 面板（CSS + JS 内联）
│   ├── manifest.json         # PWA 清单
│   └── sw.js                 # Service Worker（离线缓存）
├── assets/
│   └── logo.svg              # 矢量 Logo（靛蓝→粉红渐变）
├── generate_logo.py          # Logo + 全尺寸图标生成器
├── batch_transcribe.py       # 视频口播 Whisper 语音识别
├── install.bat               # 桌面快捷方式安装器
├── setup_autostart.bat       # 开机自启管理工具
└── launch_doutracker.vbs     # 静默后台启动器
```

---

## 🔌 API 端点

| 方法 | 路径 | 功能 |
|------|------|------|
| `POST` | `/api/scrape` | 启动抓取任务（异步） |
| `GET` | `/api/progress` | 抓取进度轮询 |
| `GET` | `/api/bloggers` | 博主列表 |
| `GET` | `/api/bloggers/{id}` | 博主详情 + 视频列表 |
| `GET` | `/api/bloggers/{id}/videos` | 视频排序/分页 |
| `GET` | `/api/bloggers/{id}/stats` | 聚合统计 |
| `DELETE` | `/api/bloggers/{id}` | 删除博主及视频 |
| `GET` | `/api/export/{id}` | 导出 JSON / CSV |
| `GET` | `/api/dashboard` | 全局仪表盘数据 |
| `GET/POST` | `/api/settings` | Cookie / 设置管理 |
| `GET` | `/api/autostart` | 开机自启状态 |
| `POST` | `/api/autostart/toggle` | 切换开机自启 |

---

## 🛠 技术栈

- **后端**: Python 3.10+ · FastAPI · Uvicorn · curl_cffi · SQLite
- **前端**: 纯 HTML/CSS/JS（零依赖框架）· PWA · Service Worker
- **Logo**: SVG · Pillow（图标生成）
- **语音**: openai-whisper（可选，口播识别）

---

## 📄 License

MIT
