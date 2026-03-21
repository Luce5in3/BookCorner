# BookCorner · Frontend 开发提示词

> Vue3 + Vite + Element Plus | Pinia | Axios | 前后端分离

---

## 技术栈

- Vue 3 + Vite
- 状态管理：Pinia
- 路由：Vue Router 4
- UI 组件库：Element Plus
- HTTP 请求：Axios（统一封装拦截器）
- CSS 工具：TailwindCSS

---

## 项目目录结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                      # 接口请求层（按模块拆分）
│   │   ├── request.js            # Axios 实例 + 拦截器
│   │   ├── auth.js               # 登录、注册、刷新 token
│   │   ├── books.js              # 图书、分类、副本
│   │   ├── borrows.js            # 借阅、续借、还书
│   │   ├── reservations.js       # 预约
│   │   ├── fines.js              # 罚款
│   │   └── announcements.js      # 公告
│   ├── assets/                   # 静态资源
│   │   ├── images/
│   │   └── styles/
│   │       └── global.css
│   ├── components/               # 公共组件
│   │   ├── AppHeader.vue
│   │   ├── AppSidebar.vue
│   │   └── AppFooter.vue
│   ├── layouts/                  # 布局组件
│   │   ├── AdminLayout.vue       # 管理员布局（含侧边栏）
│   │   └── UserLayout.vue        # 读者布局
│   ├── router/
│   │   └── index.js              # 路由配置 + 角色守卫
│   ├── stores/                   # Pinia 状态管理
│   │   ├── auth.js               # 用户信息、token 持久化
│   │   ├── books.js
│   │   └── borrows.js
│   ├── views/                    # 页面组件（按角色拆分）
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── reader/               # 读者端页面
│   │   │   ├── Home.vue          # 首页 / 书目浏览
│   │   │   ├── BookDetail.vue    # 图书详情
│   │   │   ├── MyBorrows.vue     # 我的借阅
│   │   │   ├── MyReservations.vue# 我的预约
│   │   │   └── MyFines.vue       # 我的罚款
│   │   └── admin/                # 管理员端页面
│   │       ├── Dashboard.vue     # 数据总览
│   │       ├── BookManage.vue    # 图书管理
│   │       ├── CopyManage.vue    # 副本管理
│   │       ├── BorrowManage.vue  # 借阅管理
│   │       ├── UserManage.vue    # 用户管理
│   │       ├── FineManage.vue    # 罚款管理
│   │       └── Announcements.vue # 公告管理
│   ├── utils/
│   │   ├── token.js              # token 存取（localStorage）
│   │   └── format.js             # 日期、金额格式化
│   ├── App.vue
│   └── main.js
├── .env.development              # 开发环境变量
├── .env.production               # 生产环境变量
├── index.html
├── vite.config.js
└── package.json
```

---

## 环境变量

```ini
# .env.development
VITE_API_BASE_URL=http://127.0.0.1:8000

# .env.production
VITE_API_BASE_URL=https://your-production-domain.com
```

---

## 后端接口对照表

| 模块 | 接口前缀 | 说明 |
|------|---------|------|
| 认证 | `/api/auth/` | 登录、注册、刷新 token |
| 用户 | `/api/users/` | 用户管理、个人信息 |
| 分类 | `/api/categories/` | 树形分类 |
| 图书 | `/api/books/` | 图书 CRUD、搜索 |
| 副本 | `/api/copies/` | 实体书管理 |
| 借阅 | `/api/borrows/` | 借书、还书、续借 |
| 预约 | `/api/reservations/` | 预约、取消 |
| 罚款 | `/api/fines/` | 罚款查询、缴清 |
| 公告 | `/api/announcements/` | 公告列表、管理 |

### 统一响应格式

```json
// 成功
{ "code": 200, "message": "success", "data": { ... } }

// 分页
{ "code": 200, "message": "success",
  "data": { "count": 100, "next": "...", "previous": "...", "results": [...] } }

// 失败
{ "code": 400, "message": "参数错误", "data": null }
```

---

## 路由设计

```
/login                    登录页
/register                 注册页

/reader/                  读者端（需登录，role=0）
  home                    首页 / 书目浏览
  book/:id                图书详情
  borrows                 我的借阅
  reservations            我的预约
  fines                   我的罚款

/admin/                   管理员端（需登录，role≥1）
  dashboard               数据总览
  books                   图书管理
  copies                  副本管理
  borrows                 借阅管理
  users                   用户管理
  fines                   罚款管理
  announcements           公告管理
```

---

## 开发任务（按顺序执行）

### Step 1 — 项目初始化
1. `npm create vite@latest frontend -- --template vue`
2. 安装依赖：`element-plus`、`pinia`、`vue-router`、`axios`、`tailwindcss`
3. 配置 `vite.config.js`：路径别名 `@`、开发代理 `/api → http://127.0.0.1:8000`

### Step 2 — Axios 封装（`src/api/request.js`）
1. 创建 Axios 实例，`baseURL` 读取 `VITE_API_BASE_URL`
2. 请求拦截器：自动在 Header 注入 `Authorization: Bearer <access_token>`
3. 响应拦截器：
   - 统一解构 `{ code, message, data }`
   - `code !== 200` 时 `ElMessage.error(message)` 并 reject
   - `401` 时自动用 refresh token 换新 access token，失败则跳转登录页

### Step 3 — Pinia 状态管理（`src/stores/auth.js`）
1. state：`userInfo`、`accessToken`、`refreshToken`
2. 持久化：token 存 `localStorage`，页面刷新后自动还原
3. actions：`login()`、`logout()`、`refreshToken()`、`fetchUserInfo()`
4. getters：`isLoggedIn`、`isAdmin`、`isSuperAdmin`

### Step 4 — 路由与守卫（`src/router/index.js`）
1. 按上述路由表配置所有路由，配置 `meta.requiresAuth` 和 `meta.role`
2. 全局前置守卫：
   - 未登录访问需鉴权页面 → 跳转 `/login`
   - 已登录访问 `/login` → 按角色跳转对应首页
   - 角色不匹配 → 跳转 403 页面

### Step 5 — 布局组件
1. `AdminLayout.vue`：Element Plus `el-container` 布局，左侧 `el-menu` 导航，顶部显示用户名和退出按钮
2. `UserLayout.vue`：顶部导航栏 + 内容区，简洁风格

### Step 6 — 认证页面
1. `Login.vue`：用户名 + 密码表单，登录成功后按角色跳转
2. `Register.vue`：用户名、密码、真实姓名、邮箱，注册成功跳转登录

### Step 7 — 读者端页面
1. `Home.vue`：图书列表，支持关键词搜索、分类筛选、分页，卡片展示封面/书名/作者/可借数
2. `BookDetail.vue`：图书详情，显示完整信息，提供借阅 / 预约按钮
3. `MyBorrows.vue`：借阅记录表格，显示状态、应还时间，提供续借按钮
4. `MyReservations.vue`：预约记录，提供取消按钮
5. `MyFines.vue`：罚款列表，显示金额、状态

### Step 8 — 管理员端页面
1. `Dashboard.vue`：统计卡片（总图书数、今日借阅、逾期数、待缴罚款），可用 ECharts 或 Element Plus 图表
2. `BookManage.vue`：图书列表表格，支持新增/编辑/上下架，弹窗表单
3. `CopyManage.vue`：副本列表，支持入库、修改状态
4. `BorrowManage.vue`：借阅列表，支持办理借出/归还，逾期高亮
5. `UserManage.vue`：用户列表，支持禁用/启用、修改角色
6. `FineManage.vue`：罚款列表，支持标记已缴/免除
7. `Announcements.vue`：公告列表，支持新增/编辑/发布/下架

---

## 规范约束

- 所有 API 调用统一走 `src/api/` 对应模块，禁止在组件内直接使用 `axios`
- 表单校验统一使用 Element Plus `el-form` 的 `rules`
- 时间格式化统一使用 `src/utils/format.js`，推荐 `dayjs`
- 金额显示保留两位小数，单位"元"
- 状态码对应文字统一维护在各模块 `api/*.js` 的常量中
- 组件命名使用 PascalCase，文件名与组件名一致

---

## 当前任务

请先完成 **Step 1 + Step 2 + Step 3 + Step 4**，输出：

1. `vite.config.js`（含代理配置和路径别名）
2. `src/api/request.js`（Axios 封装，含 JWT 自动刷新）
3. `src/stores/auth.js`（Pinia，含 token 持久化）
4. `src/router/index.js`（全部路由 + 角色守卫）
5. `src/utils/token.js`
6. `src/utils/format.js`
7. `package.json`（列出所有依赖）
