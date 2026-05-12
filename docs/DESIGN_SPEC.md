# TodoApp 设计规范 v1.0

## 一、设计理念

### 核心原则
- **少即是多** — 每个页面只做一件事，减少认知负担
- **内容优先** — 任务内容本身是最重要的视觉元素，装饰服务于功能
- **触手可及** — 核心操作不超过2次点击，主操作按钮固定在拇指热区
- **安静陪伴** — 不做焦虑营销，用柔和反馈传递"完成"的愉悦感

### 品牌调性
- 冷静而温暖，专业但不冰冷
- 不制造焦虑（不用红色标记未完成数量）
- 已完成任务的视觉消失感（划线淡出）带来满足感

---

## 二、色彩系统

### Light Mode（浅色模式）

| Token | 色值 | 用途 |
|---|---|---|
| `--color-bg-primary` | `#FFFFFF` | 主背景 |
| `--color-bg-secondary` | `#F5F5F7` | 次级背景（分组卡片） |
| `--color-bg-tertiary` | `#EBEBED` | 输入框背景 |
| `--color-text-primary` | `#1D1D1F` | 主文字 |
| `--color-text-secondary` | `#6E6E73` | 辅助文字 |
| `--color-text-tertiary` | `#AEAEB2` | 占位文字/禁用态 |
| `--color-accent` | `#007AFF` | 主强调色（按钮/链接） |
| `--color-accent-hover` | `#0056CC` | 悬停态 |
| `--color-success` | `#34C759` | 完成/成功 |
| `--color-warning` | `#FF9500` | 即将到期 |
| `--color-danger` | `#FF3B30` | 已过期/删除 |
| `--color-separator` | `#E5E5EA` | 分割线 |

### Dark Mode（深色模式）

| Token | 色值 | 用途 |
|---|---|---|
| `--color-bg-primary` | `#000000` | 主背景 |
| `--color-bg-secondary` | `#1C1C1E` | 次级背景 |
| `--color-bg-tertiary` | `#2C2C2E` | 输入框背景 |
| `--color-text-primary` | `#F5F5F7` | 主文字 |
| `--color-text-secondary` | `#98989D` | 辅助文字 |
| `--color-text-tertiary` | `#636366` | 占位文字/禁用态 |
| `--color-accent` | `#0A84FF` | 主强调色 |
| `--color-accent-hover` | `#409CFF` | 悬停态 |
| `--color-success` | `#30D158` | 完成/成功 |
| `--color-warning` | `#FF9F0A` | 即将到期 |
| `--color-danger` | `#FF453A` | 已过期/删除 |
| `--color-separator` | `#38383A` | 分割线 |

### 优先级语义色彩

| 优先级 | 颜色 | 色值 |
|---|---|---|
| P1 - 紧急 | 红色 | `#FF3B30` / `#FF453A` |
| P2 - 重要 | 橙色 | `#FF9500` / `#FF9F0A` |
| P3 - 普通 | 蓝色 | `#007AFF` / `#0A84FF` |
| P4 - 低 | 灰色 | `#8E8E93` / `#636366` |

### 清单颜色（8色预设）
```
#007AFF(蓝) #FF9500(橙) #34C759(绿) #FF3B30(红)
#AF52DE(紫) #FF2D55(粉) #00C7BE(青) #8E8E93(灰)
```

---

## 三、字体系统

### 字体族

| 平台 | 字体 | 后备字体 |
|---|---|---|
| iOS | SF Pro Display / SF Pro Text | -apple-system |
| Windows | Segoe UI Variable | Segoe UI, sans-serif |
| 通用 | Inter（应用内嵌字体） | system-ui |

### 字号与行高（iOS基准 / Windows等比缩放）

| Token | 字号 | 行高 | 字重 | 用途 |
|---|---|---|---|---|
| `caption` | 11px | 14px | 400 | 辅助信息/时间戳 |
| `caption-bold` | 11px | 14px | 600 | 标签/徽章 |
| `body-small` | 13px | 18px | 400 | 备注/子任务 |
| `body` | 15px | 21px | 400 | 任务标题/正文 |
| `body-bold` | 15px | 21px | 600 | 清单名称/强调 |
| `subhead` | 17px | 24px | 400 | 次级标题 |
| `title` | 20px | 28px | 700 | 页面标题 |
| `large-title` | 28px | 36px | 700 | "今天"大标题 |

---

## 四、间距系统（8px基准网格）

| Token | 值 | 用途 |
|---|---|---|
| `space-xxs` | 4px | 紧密元素间距 |
| `space-xs` | 8px | 图标与文字间距 |
| `space-sm` | 12px | 列表项内边距 |
| `space-md` | 16px | 标准边距/卡片内边距 |
| `space-lg` | 24px | 区块间距 |
| `space-xl` | 32px | 页面级内边距 |
| `space-xxl` | 48px | 大区块分隔 |

### 圆角

| Token | 值 | 用途 |
|---|---|---|
| `radius-sm` | 6px | 标签/徽章/小组件 |
| `radius-md` | 10px | 卡片/列表项 |
| `radius-lg` | 14px | 大卡片/面板 |
| `radius-full` | 999px | 按钮/头像/药丸标签 |

---

## 五、图标系统

### 技术选型
- 使用 **Material Symbols** (Google) 的 Rounded 风格
- 图标尺寸：20px（标准）、24px（导航栏）、16px（内联）
- 全部使用 SVG，支持动态着色

### 核心图标集

| 功能 | 图标名称 | 用途 |
|---|---|---|
| 导航-今天 | `today` | Tab "今天" |
| 导航-清单 | `checklist` | Tab "清单" |
| 导航-日历 | `calendar_month` | Tab "日历" |
| 导航-统计 | `bar_chart` | Tab "统计" |
| 导航-设置 | `settings` | Tab "设置" |
| 操作-添加 | `add` | 创建任务 FAB |
| 操作-完成 | `check_circle` | 完成任务 |
| 操作-未完成 | `radio_button_unchecked` | 未完成任务 |
| 操作-删除 | `delete_outline` | 删除任务 |
| 操作-更多 | `more_horiz` | 更多操作 |
| 操作-搜索 | `search` | 搜索入口 |
| 操作-排序 | `sort` | 排序切换 |
| 状态-到期 | `schedule` | 截止日期 |
| 状态-提醒 | `notifications` | 提醒设置 |
| 状态-重复 | `repeat` | 重复任务 |
| 状态-子任务 | `subdirectory_arrow_right` | 子任务缩进 |
| 清单 | `list_alt` | 清单图标 |
| 标签 | `label` | 标签图标 |
| 优先级 | `flag` | 优先级标记 |
| 番茄钟 | `timer` | 专注计时 |
| 习惯 | `trending_up` | 习惯追踪 |
| 空白状态 | `task_alt` | 全部完成插画 |

### 图标使用规则
- NavBar图标：24px，未选中用 outlined 变体，选中用 filled 变体
- 行内操作图标：20px，颜色跟随 `--color-text-secondary`
- 状态指示图标：16px，使用语义色

---

## 六、组件库

### 1. TaskItem（任务列表项）

```
┌──────────────────────────────────────────────┐
│ ○  任务标题                            ⋮    │
│    ├ 子任务 #1                    ○         │
│    └ 子任务 #2                    ○         │
│    📅 今天   🏷 工作   🚩 P2              │
└──────────────────────────────────────────────┘
```

**状态变体：**
- `default` — 正常未完成：radio_button_unchecked + 正常字重
- `completed` — 已完成：check_circle (green) + 删除线 + 透明度0.5
- `overdue` — 已过期：日期变红色 + 左侧红色指示条
- `due-today` — 今天到期：日期橙色
- `dragging` — 拖拽中：轻微阴影 + 缩放1.02

**交互动效：**
- 点击圆圈完成：check_circle 弹性缩放动画 (spring: 0.4s)
- 完成任务：任务本身上滑淡出 (0.3s ease-out, 延迟0.2s)
- 左滑：显示删除/更多按钮 (iOS风格)
- 长按：触发拖拽排序 (触觉反馈)

### 2. FAB（浮动操作按钮）

```
┌──────┐
│  +   │  尺寸: 56x56px, 圆角: 28px
│  新增  │  颜色: --color-accent
└──────┘  阴影: 0 4px 12px rgba(0,0,0,0.15)
           位置: 右下角, 距边缘 24px
```

**展开状态（iOS风格）：**
```
点击FAB后弹出快速创建面板：
┌──────────────────────────────┐
│  📝 在"工作"中新建任务        │
│  ┌──────────────────────────┐ │
│  │ 输入任务名称...           │ │
│  └──────────────────────────┘ │
│  📅 截止日期   🚩 优先级     │
│  🏷 标签       🔄 重复       │
│  ┌─────────┐                │
│  │   创建   │  → 主按钮      │
│  └─────────┘                │
└──────────────────────────────┘
```

### 3. ListCard（清单卡片）

```
┌──────────────────────────────────────┐
│  ● 工作                      3/12   │
│  ┌──────────────────────────────┐   │
│  │ ○ 完成Q2报告                │   │
│  │ ✓ 发送周报                  │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

- 圆角卡片 10px，背景 `--color-bg-secondary`
- 左侧彩色圆点表示清单颜色
- 右侧显示进度 "已完成/总数"
- 最多预览3条未完成任务

### 4. EmptyState（空状态）

```
┌──────────────────────────────┐
│                              │
│         🎉 (插画)            │
│     今天没有待办任务了        │
│    去喝杯咖啡吧 ☕            │
│                              │
│    ┌──────────────┐          │
│    │   创建新任务   │          │
│    └──────────────┘          │
└──────────────────────────────┘
```

- 当"今天"视图无任务时显示
- 已完成全部任务时显示庆祝动画（Confetti动画 2s）
- 引导用户创建新任务或查看其他视图

### 5. NavigationBar（底部导航栏）

```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│   📅    │   ✓     │   📆    │   📊    │   ⚙️    │
│  今天   │  清单   │  日历   │  统计   │  设置   │
└─────────┴─────────┴─────────┴─────────┴─────────┘
```

- iOS风格：磨砂玻璃背景 (Blur: 20px)
- Windows风格：`--color-bg-secondary` 纯色背景
- 选中态：Accent色图标 + 微字重加粗
- 5个Tab，不可滚动

### 6. Modal Sheet（底部弹出面板）

- 从底部滑入，高度自适应
- 顶部拖拽指示条（灰色小横条，36x5px）
- 背景遮罩：黑色50%透明度
- 支持手势下滑关闭
- 用于：新建任务 / 任务详情 / 筛选器 / 日期选择

### 7. Toast / SnackBar（提示）

```
┌─────────────────────────────────┐
│ ✓  任务已完成                    │
└─────────────────────────────────┘
```

- 顶部浮现，自动消失3s
- 类型：success(绿) / warning(橙) / error(红) / info(蓝)
- 动画：从顶部滑入 → 停留 → 上滑消失

---

## 七、页面布局（iOS基准 / Windows自适应）

### 导航架构

```
[启动页/登录]
     │
     ▼
┌──────────────────────────────────────┐
│  NavigationBar (5 Tabs)              │
│  今天 │ 清单 │ 日历 │ 统计 │ 设置    │
├──────────────────────────────────────┤
│                                      │
│  Page Content                        │
│  (ScrollView / ListView)             │
│                                      │
│                                      │
│                                [FAB] │
├──────────────────────────────────────┤
│  Bottom Safe Area                    │
└──────────────────────────────────────┘
```

### 布局适配规则

| 属性 | iOS (Phone) | Windows (Desktop) |
|---|---|---|
| 最大内容宽度 | 全屏宽度 | 800px居中 |
| 列数 | 1列 | 可多列（日历视图2列） |
| 侧边栏 | 无 | 可选（宽屏>1200px时显示清单列表侧边栏） |
| 导航位置 | 底部TabBar | 左侧Rail / 底部TabBar |
| FAB位置 | 右下角 | 右下角 |

### 响应式断点

| 断点 | 宽度 | 适配行为 |
|---|---|---|
| Compact | < 600px | 手机布局，单列 |
| Medium | 600-1200px | 平板布局，可选双列 |
| Expanded | > 1200px | 桌面布局，侧边栏+双列内容 |

---

## 八、动效规范

### 转场动画

| 转场 | 动画 | 时长 | 缓动 |
|---|---|---|---|
| Push（进入详情） | 从右滑入 | 300ms | ease-out |
| Pop（返回） | 从左滑出 | 250ms | ease-in |
| Modal（底部弹出） | 从下滑入 | 350ms | spring(0.8) |
| 页面切换（Tab） | 交叉淡入淡出 | 200ms | ease |
| 新建任务 | 从FAB位置展开 | 350ms | spring(0.7) |

### 微交互

| 交互 | 动画 |
|---|---|
| 任务完成 | checkbox弹性缩放 + 划线渐现 + 条目淡出 |
| 下拉刷新 | Material风格圆环 + 回弹 |
| 删除任务 | 左滑出现红色按钮 + 确认后整行收起 |
| 切换清单 | 清单列表推入，任务列表淡入 |
| 日历拖拽 | 任务卡片跟随手指 + 目标日期高亮 |
| 空状态到有内容 | 插画淡出 + 内容从下淡入 |

### 动画原则
- 所有动画时长不超过 400ms
- 自然弹簧阻尼（spring: mass=1, stiffness=200, damping=20）
- 尊重系统"减少动态效果"辅助功能设置
- 列表项添加/删除使用 AnimatedList 的渐进动画

---

## 九、触觉反馈（iOS）

| 场景 | 反馈类型 |
|---|---|
| 任务完成 | `UIImpactFeedbackGenerator.light` |
| 长按拖拽开始 | `UIImpactFeedbackGenerator.medium` |
| 拖拽放下 | `UIImpactFeedbackGenerator.rigid` |
| 删除确认 | `UINotificationFeedbackGenerator.warning` |
| 刷新完成 | `UINotificationFeedbackGenerator.success` |

---

## 十、无障碍规范

- 所有交互元素最小触摸区域：44x44pt（iOS HIG标准）
- 色彩对比度至少达到 WCAG AA 级（正文 4.5:1，大文字 3:1）
- 支持 Dynamic Type 字号缩放（iOS）和 Windows 缩放
- 所有图标和图片提供语义化 label
- 支持 VoiceOver / 讲述人 导航顺序
- 操作结果提供 screen reader 播报

---

## 十一、App Icon 设计规范

### 主图标
- 风格：SF Symbols 风格 + 渐变背景
- 元素：勾选符号 ✓ + 轻微3D卡片效果
- 背景渐变：--color-accent → --color-success 的对角线渐变
- 底色：iOS 使用白色底，Windows 使用 Accent 色底

### 平台导出尺寸

| 平台 | 尺寸 | 格式 |
|---|---|---|
| iOS App Icon | 1024x1024 | PNG |
| iOS Spotlight | 80x80, 120x120 | PNG |
| iOS Settings | 58x58, 87x87 | PNG |
| iOS Notification | 40x40, 60x60 | PNG |
| Windows Store | 44x44 ~ 310x310 | PNG (11 sizes) |
| Windows Taskbar | 32x32, 48x48 | ICO |

---

## 十二、设计交付清单

### Figma / 设计稿需要包含：
- [ ] Light Mode 完整设计稿（5个主页面）
- [ ] Dark Mode 完整设计稿（5个主页面）
- [ ] 组件库（TaskItem / FAB / ListCard / Modal / Toast / EmptyState）
- [ ] 交互原型（任务创建 → 完成 → 空状态 完整流程）
- [ ] App Icon 设计稿
- [ ] 启动页 / Onboarding 引导页
- [ ] 各状态变体（加载 / 空 / 错误 / 完成）

---

## 附录：参考设计语言

- **Apple Human Interface Guidelines** — 操作反馈、触觉、导航范式
- **Material Design 3** — 色彩 Token 体系、动效规范
- **Linear App** — 现代简约待办/项目管理设计标杆
- **Things 3** — iOS 待办设计天花板、交互细节
- **Todoist** — 过滤器/标签 信息架构参考
