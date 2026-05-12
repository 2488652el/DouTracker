# TodoApp 开发文档 v1.0

## 一、技术架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层 (Flutter)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────────┐ │
│  │   iOS App   │ │ Windows App │ │        Web App (可选)      │ │
│  └──────┬──────┘ └──────┬──────┘ └──────────────┬────────────┘ │
│         │               │                        │              │
├─────────┴───────────────┴────────────────────────┴──────────────┤
│                        共享业务层 (Dart)                         │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐  │
│  │ 状态管理 │ │ 同步引擎 │ │ 本地存储 │ │ 通知服务 │ │ 网络层  │  │
│  │Riverpod │ │  CRDT   │ │  Isar    │ │LocalPush│ │ Dio     │  │
│  └─────────┘ └─────────┘ └──────────┘ └─────────┘ └─────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                         后端服务层                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────┐ │
│  │   API网关    │ │   用户服务   │ │   任务服务   │ │ 同步服务 │ │
│  │  (Dart Shelf)│ │   (Auth)     │ │  (Tasks)     │ │ (CRDT)  │ │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └────┬────┘ │
│         │                │                │                │     │
├─────────┴────────────────┴────────────────┴────────────────┴─────┤
│                        数据存储层                                │
│              ┌──────────────┐    ┌──────────┐                   │
│              │ PostgreSQL   │    │  Redis   │                   │
│              │ (任务/用户)   │    │ (缓存/队列)│                   │
│              └──────────────┘    └──────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层级 | 技术 | 版本 | 选型理由 |
|---|---|---|---|
| **框架** | Flutter | 3.32+ | 跨平台iOS+Windows原生支持，性能优异 |
| **状态管理** | Riverpod | 2.3+ | 编译时安全，依赖注入，测试友好 |
| **本地数据库** | Isar | 3.1+ | 高性能NoSQL，支持全文搜索，跨平台 |
| **网络请求** | Dio | 5.4+ | Dart生态最成熟的HTTP库，支持拦截器 |
| **同步方案** | CRDT | 自定义 | 离线优先，自动冲突合并 |
| **后端框架** | Dart Shelf | 1.4+ | 与前端语言统一，轻量高性能 |
| **数据库** | PostgreSQL | 16+ | 可靠，支持JSONB，适合CRDT操作日志 |
| **缓存** | Redis | 7.2+ | 会话管理，同步队列，实时推送 |
| **认证** | JWT | - | 无状态，跨平台兼容 |

---

## 二、目录结构

### 2.1 项目根目录

```
todoapp/
├── .github/                  # GitHub Actions CI/CD
│   └── workflows/
│       ├── build_ios.yml
│       └── build_windows.yml
├── android/                  # Android 原生配置 (暂不开发)
├── ios/                      # iOS 原生配置
│   ├── Runner/
│   ├── Runner.xcodeproj/
│   └── Flutter/
├── windows/                  # Windows 原生配置
│   ├── runner/
│   ├── flutter/
│   └── CMakeLists.txt
├── lib/                      # Dart 源代码
│   ├── main.dart             # 应用入口
│   ├── app.dart              # App根组件
│   ├── core/                 # 核心模块
│   │   ├── constants/        # 常量定义
│   │   ├── errors/           # 错误处理
│   │   ├── services/         # 核心服务
│   │   └── utils/            # 工具函数
│   ├── features/             # 业务功能模块
│   │   ├── auth/             # 用户认证
│   │   ├── tasks/            # 任务管理
│   │   ├── lists/            # 清单管理
│   │   ├── calendar/         # 日历视图
│   │   ├── statistics/       # 数据统计
│   │   └── settings/         # 设置页面
│   ├── presentation/         # 展示层
│   │   ├── components/       # 可复用组件
│   │   ├── pages/            # 页面组件
│   │   └── widgets/          # 基础widgets
│   ├── providers/            # Riverpod providers
│   └── shared/               # 共享代码
├── test/                     # 单元测试
│   ├── unit/                 # 单元测试
│   └── integration/          # 集成测试
├── assets/                   # 静态资源
│   ├── icons/                # 图标
│   ├── images/               # 图片
│   └── fonts/                # 字体
├── pubspec.yaml              # 依赖管理
└── analysis_options.yaml     # 代码分析配置
```

### 2.2 关键目录职责

| 目录 | 职责 |
|---|---|
| `lib/core/` | 全局常量、错误处理、工具函数、核心服务 |
| `lib/features/` | 按功能模块划分，包含UI、业务逻辑、数据层 |
| `lib/presentation/` | 纯展示组件，无业务逻辑 |
| `lib/providers/` | Riverpod状态管理定义 |
| `test/unit/` | 纯函数/类的单元测试 |
| `test/integration/` | 多模块集成测试 |

---

## 三、数据模型

### 3.1 核心实体

#### User（用户）

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | `String` | 主键，UUID | 用户唯一标识 |
| `email` | `String` | 非空，唯一 | 邮箱地址 |
| `phone` | `String?` | 可选 | 手机号码 |
| `name` | `String` | 非空 | 显示名称 |
| `avatar_url` | `String?` | 可选 | 头像URL |
| `created_at` | `DateTime` | 非空 | 创建时间 |
| `updated_at` | `DateTime` | 非空 | 更新时间 |
| `last_sync_at` | `DateTime?` | 可选 | 最后同步时间 |

#### Task（任务）

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | `String` | 主键，UUID | 任务唯一标识 |
| `user_id` | `String` | 外键 | 所属用户 |
| `list_id` | `String` | 外键 | 所属清单 |
| `title` | `String` | 非空，max=200 | 任务标题 |
| `description` | `String?` | 可选 | 任务备注 |
| `priority` | `Priority` | 枚举：P1-P4 | 优先级 |
| `due_date` | `DateTime?` | 可选 | 截止日期（含时间） |
| `reminder_at` | `DateTime?` | 可选 | 提醒时间 |
| `repeat_rule` | `RepeatRule?` | 可选 | 重复规则 |
| `completed_at` | `DateTime?` | 可选 | 完成时间 |
| `is_completed` | `bool` | 默认false | 是否已完成 |
| `order` | `int` | 默认0 | 排序序号 |
| `created_at` | `DateTime` | 非空 | 创建时间 |
| `updated_at` | `DateTime` | 非空 | 更新时间 |

#### Subtask（子任务）

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | `String` | 主键，UUID | 子任务唯一标识 |
| `task_id` | `String` | 外键 | 所属任务 |
| `title` | `String` | 非空，max=100 | 子任务标题 |
| `is_completed` | `bool` | 默认false | 是否已完成 |
| `order` | `int` | 默认0 | 排序序号 |

#### TaskList（清单）

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | `String` | 主键，UUID | 清单唯一标识 |
| `user_id` | `String` | 外键 | 所属用户 |
| `name` | `String` | 非空，max=50 | 清单名称 |
| `color` | `String` | 非空 | 颜色十六进制值 |
| `is_archived` | `bool` | 默认false | 是否已归档 |
| `order` | `int` | 默认0 | 排序序号 |
| `created_at` | `DateTime` | 非空 | 创建时间 |
| `updated_at` | `DateTime` | 非空 | 更新时间 |

#### Tag（标签）

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | `String` | 主键，UUID | 标签唯一标识 |
| `user_id` | `String` | 外键 | 所属用户 |
| `name` | `String` | 非空，max=30 | 标签名称 |
| `color` | `String` | 非空 | 颜色十六进制值 |

#### TaskTag（任务-标签关联）

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `task_id` | `String` | 外键 | 任务ID |
| `tag_id` | `String` | 外键 | 标签ID |

### 3.2 枚举定义

#### Priority（优先级）
```dart
enum Priority {
  p1,  // 紧急
  p2,  // 重要
  p3,  // 普通
  p4,  // 低
}
```

#### RepeatRule（重复规则）
```dart
enum RepeatFrequency {
  daily,
  weekly,
  monthly,
  yearly,
  custom,
}

class RepeatRule {
  final RepeatFrequency frequency;
  final List<int>? daysOfWeek;  // 每周几 [1-7]
  final int? dayOfMonth;        // 每月几号
  final DateTime? endDate;      // 结束日期
  final int? maxOccurrences;    // 最大重复次数
}
```

---

## 四、API接口设计

### 4.1 认证接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/refresh` | 刷新Token |
| POST | `/api/auth/logout` | 用户登出 |
| GET | `/api/auth/me` | 获取当前用户信息 |

#### POST /api/auth/register
**请求体：**
```json
{
  "email": "string",
  "password": "string",
  "name": "string",
  "phone": "string (可选)"
}
```

**成功响应 (201)：**
```json
{
  "user": {
    "id": "uuid",
    "email": "string",
    "name": "string",
    "created_at": "datetime"
  },
  "access_token": "string",
  "refresh_token": "string"
}
```

#### POST /api/auth/login
**请求体：**
```json
{
  "email": "string",
  "password": "string"
}
```

**成功响应 (200)：** 同上

### 4.2 任务接口

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/api/tasks` | 获取任务列表 |
| GET | `/api/tasks/{id}` | 获取单个任务 |
| POST | `/api/tasks` | 创建任务 |
| PUT | `/api/tasks/{id}` | 更新任务 |
| DELETE | `/api/tasks/{id}` | 删除任务 |
| POST | `/api/tasks/{id}/complete` | 完成/取消完成任务 |

#### GET /api/tasks
**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `list_id` | String | 否 | 按清单筛选 |
| `completed` | bool | 否 | 按完成状态筛选 |
| `due_date_start` | DateTime | 否 | 截止日期范围开始 |
| `due_date_end` | DateTime | 否 | 截止日期范围结束 |
| `priority` | String | 否 | 按优先级筛选 |
| `page` | int | 否 | 页码，默认1 |
| `limit` | int | 否 | 每页数量，默认20 |

**成功响应 (200)：**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "priority": "p1",
      "due_date": "datetime",
      "is_completed": false,
      "list_id": "uuid",
      "list_name": "string",
      "subtasks": [
        {"id": "uuid", "title": "string", "is_completed": false}
      ],
      "tags": ["tag1", "tag2"],
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

#### POST /api/tasks
**请求体：**
```json
{
  "title": "string (必填)",
  "description": "string (可选)",
  "list_id": "string (必填)",
  "priority": "p1-p4 (可选，默认p3)",
  "due_date": "datetime (可选)",
  "reminder_at": "datetime (可选)",
  "repeat_rule": {
    "frequency": "daily/weekly/monthly/yearly/custom",
    "days_of_week": [1,3,5],
    "end_date": "datetime"
  },
  "subtasks": [
    {"title": "string"}
  ],
  "tags": ["tag_id1", "tag_id2"]
}
```

### 4.3 清单接口

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/api/lists` | 获取清单列表 |
| GET | `/api/lists/{id}` | 获取单个清单（含任务） |
| POST | `/api/lists` | 创建清单 |
| PUT | `/api/lists/{id}` | 更新清单 |
| DELETE | `/api/lists/{id}` | 删除清单 |

### 4.4 同步接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/sync/pull` | 拉取变更（从服务器获取更新） |
| POST | `/api/sync/push` | 推送变更（上传本地操作） |

#### POST /api/sync/pull
**请求体：**
```json
{
  "last_sync_at": "datetime",
  "client_id": "string (客户端唯一标识)"
}
```

**成功响应 (200)：**
```json
{
  "tasks": [...],
  "lists": [...],
  "tags": [...],
  "sync_id": "string",
  "server_time": "datetime"
}
```

#### POST /api/sync/push
**请求体：**
```json
{
  "operations": [
    {
      "type": "create/update/delete",
      "entity": "task/list/tag",
      "data": {...},
      "timestamp": "datetime"
    }
  ],
  "client_id": "string"
}
```

---

## 五、状态管理

### 5.1 Provider 结构

```dart
// lib/providers/
├── auth_providers.dart     // 用户认证状态
├── task_providers.dart     // 任务状态
├── list_providers.dart     // 清单状态
├── sync_providers.dart     // 同步状态
└── ui_providers.dart       // UI状态（主题/导航等）
```

### 5.2 Auth Provider 示例

```dart
@riverpod
class Auth extends _$Auth {
  @override
  FutureOr<User?> build() async {
    // 从本地存储读取Token
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      try {
        final user = await ref.watch(authServiceProvider).getCurrentUser();
        return user;
      } catch {
        await _storage.delete(key: 'access_token');
        return null;
      }
    }
    return null;
  }

  Future<void> login(String email, String password) async {
    state = const AsyncLoading();
    final result = await ref.watch(authServiceProvider).login(email, password);
    result.when(
      success: (data) {
        await _storage.write(key: 'access_token', value: data.accessToken);
        state = AsyncData(data.user);
      },
      error: (e) {
        state = AsyncError(e, StackTrace.current);
      },
    );
  }

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    state = const AsyncData(null);
  }
}
```

### 5.3 Task Provider 示例

```dart
@riverpod
class Tasks extends _$Tasks {
  @override
  Future<List<Task>> build() async {
    final user = await ref.watch(authProvider.future);
    if (user == null) return [];
    return ref.watch(taskRepositoryProvider).getAll();
  }

  Future<void> create(Task task) async {
    await ref.watch(taskRepositoryProvider).create(task);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => ref.watch(taskRepositoryProvider).getAll());
  }

  Future<void> complete(String taskId) async {
    await ref.watch(taskRepositoryProvider).toggleComplete(taskId);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => ref.watch(taskRepositoryProvider).getAll());
  }

  Future<void> delete(String taskId) async {
    await ref.watch(taskRepositoryProvider).delete(taskId);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => ref.watch(taskRepositoryProvider).getAll());
  }
}
```

---

## 六、同步机制

### 6.1 CRDT 同步流程

```
[本地操作]                    [同步过程]                    [服务器]
    │                              │                          │
    │ 1. 创建/更新/删除任务          │                          │
    │────────────────────────────▶  │                          │
    │ 2. 写入本地Isar数据库         │                          │
    │                              │ 3. 生成操作日志           │
    │                              │    {type, entity, data, timestamp}│
    │                              │─────────────────────────▶ │
    │                              │ 4. HTTP POST /sync/push  │
    │                              │                          │ 5. CRDT合并
    │                              │◀─────────────────────────│
    │                              │ 6. 返回合并结果          │
    │                              │                          │
    │ 7. 更新本地状态               │                          │
    │◀─────────────────────────────│                          │
```

### 6.2 冲突解决策略

| 冲突场景 | 解决策略 |
|---|---|
| 两个客户端同时修改同一任务标题 | 最后写入胜出（按server_time） |
| 一方删除，另一方更新 | 删除优先 |
| 网络分区后数据不一致 | CRDT自动合并 |
| 重复创建（同一客户端离线多次创建） | 去重（按client_id+timestamp） |

### 6.3 离线支持

- 所有操作先写入本地数据库（Isar）
- 操作日志存储在本地，标记为"待同步"
- 联网后自动批量上传操作日志
- 上传成功后清除本地操作日志
- 服务端返回的变更自动更新本地数据

---

## 七、UI组件结构

### 7.1 组件层级

```
lib/presentation/
├── components/              # 业务组件
│   ├── TaskItem.dart        # 任务列表项
│   ├── TaskList.dart        # 任务列表
│   ├── TaskDetailSheet.dart # 任务详情弹窗
│   ├── ListCard.dart        # 清单卡片
│   ├── ListGrid.dart        # 清单网格
│   ├── FAB.dart             # 浮动按钮
│   ├── Toast.dart           # 提示组件
│   └── EmptyState.dart      # 空状态
├── pages/                   # 页面组件
│   ├── TodayPage.dart       # 今日视图
│   ├── ListsPage.dart       # 清单视图
│   ├── CalendarPage.dart    # 日历视图
│   ├── StatisticsPage.dart  # 统计视图
│   └── SettingsPage.dart    # 设置页面
└── widgets/                 # 基础组件
    ├── BaseAppBar.dart      # 导航栏
    ├── BaseBottomNav.dart   # 底部导航
    ├── CustomTextField.dart # 自定义输入框
    └── CustomButton.dart    # 自定义按钮
```

### 7.2 组件职责

| 组件 | 职责 | 是否有状态 |
|---|---|---|
| TaskItem | 单个任务的展示和交互 | 是（完成状态切换） |
| TaskList | 任务列表渲染，支持拖拽排序 | 是 |
| TaskDetailSheet | 任务详情编辑弹窗 | 是 |
| ListCard | 清单信息卡片，显示进度 | 否 |
| FAB | 浮动操作按钮，触发新建任务 | 是（展开/收起） |
| Toast | 全局提示组件 | 否 |

---

## 八、开发环境与构建

### 8.1 环境要求

| 工具 | 版本 | 说明 |
|---|---|---|
| Flutter | 3.32+ | 核心框架 |
| Dart | 3.4+ | 编程语言 |
| Xcode | 15+ | iOS构建工具 |
| Visual Studio | 2022+ | Windows构建工具 |
| Android Studio | Hedgehog+ | Android开发（可选） |

### 8.2 环境配置

#### iOS 配置
```bash
# 安装依赖
flutter pub get

# 进入iOS目录
cd ios

# 安装Pod依赖
pod install

# 返回项目根目录
cd ..

# 构建Release版本
flutter build ios --release
```

#### Windows 配置
```bash
# 安装依赖
flutter pub get

# 构建Release版本
flutter build windows
```

### 8.3 CI/CD 流程

```
[代码提交] → [GitHub Actions] → [构建测试] → [打包签名] → [发布]
                  │                  │              │
                  ▼                  ▼              ▼
              代码检查           iOS/Win         App Store/
              (dart analyze)     构建            Microsoft Store
```

#### GitHub Actions 关键步骤

1. **Checkout** - 拉取代码
2. **Setup Flutter** - 安装指定版本Flutter
3. **Get Dependencies** - `flutter pub get`
4. **Analyze** - `flutter analyze`
5. **Test** - `flutter test`
6. **Build iOS** - `flutter build ios`
7. **Build Windows** - `flutter build windows`
8. **Archive & Sign** - 打包签名
9. **Deploy** - 上传到应用商店

---

## 九、测试策略

### 9.1 测试分层

| 层级 | 测试类型 | 覆盖内容 |
|---|---|---|
| Unit | 单元测试 | 纯函数、数据模型、工具类 |
| Integration | 集成测试 | 多个模块协作、API调用、数据库操作 |
| Widget | Widget测试 | UI组件渲染、交互逻辑 |
| E2E | 端到端测试 | 完整用户流程 |

### 9.2 测试文件结构

```
test/
├── unit/
│   ├── models/           # 数据模型测试
│   ├── utils/            # 工具函数测试
│   └── services/         # 服务层测试
├── integration/
│   ├── auth_test.dart    # 认证流程测试
│   └── sync_test.dart    # 同步流程测试
└── widget/
    ├── task_item_test.dart   # TaskItem组件测试
    └── fab_test.dart         # FAB组件测试
```

### 9.3 测试覆盖率目标

| 模块 | 目标覆盖率 |
|---|---|
| 数据模型 | ≥ 90% |
| 工具函数 | ≥ 80% |
| 业务逻辑 | ≥ 70% |
| UI组件 | ≥ 60% |

---

## 十、代码规范

### 10.1 命名规范

| 类型 | 规范 | 示例 |
|---|---|---|
| 类名 | PascalCase | `TaskItem`, `UserRepository` |
| 函数/方法 | camelCase | `createTask`, `getUserById` |
| 变量/参数 | camelCase | `taskTitle`, `userId` |
| 常量 | SCREAMING_SNAKE_CASE | `MAX_TITLE_LENGTH`, `API_BASE_URL` |
| 文件/目录 | snake_case | `task_providers.dart`, `auth_service.dart` |
| Provider | camelCase + Provider后缀 | `tasksProvider`, `authProvider` |

### 10.2 编码风格

- 使用 `dart format` 自动格式化代码
- 使用 `dart analyze` 检查代码质量
- 每行代码不超过120字符
- 类成员顺序：构造函数 → 静态方法 → 实例方法 → getter/setter
- 函数参数不超过5个，过多时使用对象包装

### 10.3 注释规范

- 公共API必须有文档注释（`///`）
- 复杂逻辑必须有注释说明
- 注释使用中文
- 避免注释重复代码逻辑

---

## 十一、部署与发布

### 11.1 iOS 发布流程

1. **创建App ID** - 在Apple Developer Portal创建Bundle ID
2. **创建证书** - 生成Development和Distribution证书
3. **配置Provisioning Profile** - 关联证书和设备
4. **归档构建** - Xcode → Product → Archive
5. **上传到App Store Connect** - 使用Xcode或Transporter
6. **填写App信息** - 标题、描述、截图、关键词等
7. **提交审核** - 等待Apple审核（通常1-3天）

### 11.2 Windows 发布流程

1. **注册Microsoft Partner Center**
2. **创建应用** - 填写应用信息、图标、描述
3. **构建MSIX包** - `flutter build windows` → 打包工具转换
4. **提交包** - 上传到Partner Center
5. **认证测试** - Microsoft自动测试
6. **发布** - 设置发布范围和时间

### 11.3 版本号管理

- **格式**: `X.Y.Z`
- **X** - 主版本号（重大更新，不兼容）
- **Y** - 次版本号（新功能，向后兼容）
- **Z** - 修订号（bug修复）

---

## 十二、安全与隐私

### 12.1 安全措施

| 领域 | 措施 |
|---|---|
| 数据传输 | TLS 1.3加密，HSTS |
| 密码存储 | bcrypt(12 rounds)哈希 |
| Token管理 | JWT + Refresh Token，定期轮换 |
| 输入验证 | 前端+后端双重验证，防止注入攻击 |
| 权限控制 | API层做用户权限校验 |
| 敏感日志 | 禁止记录密码、Token等敏感信息 |

### 12.2 隐私合规

- 隐私政策页面，说明数据收集和使用方式
- 用户可导出/删除个人数据
- 支持用户注销账号
- 遵守GDPR和《个人信息保护法》

---

## 附录：快速开始

### 本地开发

```bash
# 1. 克隆仓库
git clone <repo-url>
cd todoapp

# 2. 安装依赖
flutter pub get

# 3. 运行iOS（需要Mac）
flutter run -d ios

# 4. 运行Windows
flutter run -d windows

# 5. 运行测试
flutter test
```

### 项目检查

```bash
# 代码分析
flutter analyze

# 代码格式化
flutter format .

# 运行所有测试
flutter test --coverage
```
