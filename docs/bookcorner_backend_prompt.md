# BookCorner · Backend 开发提示词

> Django + DRF | MySQL 8.x | JWT | 前后端分离

---

## 技术栈

- Python 3.11+
- Django 4.2 (LTS) + Django REST Framework
- MySQL 8.x（字符集 utf8mb4）
- JWT 认证：djangorestframework-simplejwt
- 跨域：django-cors-headers
- 环境变量：python-decouple
- 树形分类：django-treebeard
- 接口文档：drf-spectacular (Swagger)

---

## 项目目录结构

```
backend/
├── config/                   # 项目核心配置
│   ├── __init__.py
│   ├── urls.py               # 根路由
│   ├── wsgi.py
│   ├── asgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py           # 公共配置
│       ├── dev.py            # 开发环境
│       └── prod.py           # 生产环境
├── apps/                     # 业务 App
│   ├── users/                # 用户与认证
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py    # 自定义权限类
│   │   └── migrations/
│   ├── books/                # 图书、分类、副本
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── borrows/              # 借阅、续借
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── reservations/         # 预约
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── fines/                # 罚款
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   └── announcements/        # 公告
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── migrations/
├── utils/                    # 公共工具
│   ├── __init__.py
│   ├── response.py           # 统一响应封装
│   ├── pagination.py         # 分页配置
│   └── permissions.py        # 全局权限类
├── .env                      # 环境变量（不提交 git）
├── .env.example              # 环境变量示例
├── requirements.txt
└── manage.py
```

---

## 环境变量 .env.example

```ini
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# MySQL
DB_NAME=library_db
DB_USER=root
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=3306

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60        # 分钟
JWT_REFRESH_TOKEN_LIFETIME=7        # 天

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

## 数据库表结构（按此建 Model）

### users
- id, username(unique), password_hash(bcrypt), real_name, email(unique)
- phone, role(0=读者/1=管理员/2=超管), status(0=禁用/1=正常)
- avatar_url, created_at, updated_at
- 使用 AbstractBaseUser + PermissionsMixin 自定义用户模型

### categories（树形，django-treebeard MP_Node）
- id, name, code(unique), sort_order, created_at

### books
- id, isbn(unique), title, author, publisher, cover_url, description
- category(FK→categories), total_copies, available_copies
- price, publish_date, language(default='zh'), status(0/1)
- created_at, updated_at
- title+author 建全文索引（WITH PARSER ngram）

### book_copies
- id, book(FK→books CASCADE), barcode(unique)
- condition(1=全新/2=良好/3=一般/4=破损)
- status(0=注销/1=在馆/2=借出/3=预约锁/4=丢失)
- location, created_at, updated_at

### borrows
- id, user(FK→users), book_copy(FK→book_copies), book(FK→books 冗余)
- borrow_at, due_at, return_at, status(0=已还/1=借阅中/2=逾期/3=丢失)
- operator(FK→users nullable), remark

### renewals
- id, borrow(FK→borrows CASCADE), renewed_at, new_due_at

### reservations
- id, user(FK→users), book(FK→books)
- status(0=取消/1=等待/2=到馆/3=完成/4=过期)
- reserved_at, expire_at, notify_at, cancel_at

### fines
- id, borrow(FK→borrows), user(FK→users)
- amount(Decimal), reason(default='逾期还书')
- status(0=待缴/1=已缴/2=免除), created_at, paid_at

### announcements
- id, admin(FK→users), title, content(支持HTML)
- status(0=草稿/1=发布/2=下架), published_at, created_at

---

## 统一接口规范

### 响应格式

```json
// 成功
{ "code": 200, "message": "success", "data": { ... } }

// 分页
{ "code": 200, "message": "success",
  "data": { "count": 100, "next": "...", "previous": "...", "results": [...] } }

// 失败
{ "code": 400, "message": "参数错误", "data": null }
```

### 接口前缀

```
/api/auth/           登录、注册、刷新 token
/api/users/          用户管理
/api/categories/     分类管理
/api/books/          图书管理
/api/copies/         副本管理
/api/borrows/        借阅管理
/api/reservations/   预约管理
/api/fines/          罚款管理
/api/announcements/  公告管理
/api/schema/         Swagger 文档
```

---

## 开发任务（按顺序执行）

### Step 1 — 项目初始化
1. 创建 Django 项目，按上述目录结构组织
2. 配置 settings（开发/生产分离），连接 MySQL
3. 注册所有 App，配置 DRF、JWT、CORS、drf-spectacular

### Step 2 — Model 层
1. 按表结构创建所有 Model
2. 所有状态码用 `IntegerChoices` 枚举定义
3. 生成并执行 migrations

### Step 3 — 认证模块（users）
1. 注册、登录接口，返回 JWT access + refresh token
2. 自定义权限类：`IsReader` / `IsAdmin` / `IsSuperAdmin`
3. 接口：
   - `POST /api/auth/register`
   - `POST /api/auth/login`
   - `POST /api/auth/refresh`
   - `GET/PUT /api/users/me`

### Step 4 — 图书模块（books）
1. 分类 CRUD（管理员），返回树形结构
2. 图书 CRUD（管理员），列表支持关键词搜索、分类筛选、分页
3. 副本管理：入库、修改状态、查询

### Step 5 — 借阅模块（borrows）
1. 借书：检查 `available_copies > 0`，用 `select_for_update()` 防并发
   借出后 `book_copy.status → 2`，`books.available_copies - 1`
2. 还书：更新 `return_at`、`status → 0`，`book_copy.status → 1`，`available_copies + 1`
   若逾期自动生成 `fines` 记录
3. 续借：新增 `renewals` 记录，更新 `borrows.due_at`
4. 接口：
   - `POST /api/borrows/`
   - `POST /api/borrows/{id}/return/`
   - `POST /api/borrows/{id}/renew/`

### Step 6 — 预约模块（reservations）
1. 发起预约：同一用户同一书不能重复预约
2. 取消预约
3. 接口：
   - `POST /api/reservations/`
   - `DELETE /api/reservations/{id}/`

### Step 7 — 罚款模块（fines）
1. 查询我的罚款列表
2. 管理员标记已缴 / 免除
3. 接口：
   - `GET /api/fines/`
   - `PATCH /api/fines/{id}/`

### Step 8 — 公告模块（announcements）
1. 管理员 CRUD，发布时自动写入 `published_at`
2. 读者查询已发布公告列表
3. 接口：`/api/announcements/`

---

## 规范约束

- 时区：`Asia/Shanghai`，`USE_TZ = True`
- 密码：Django 内置 `make_password`（bcrypt）
- 分页：`PageNumberPagination`，默认每页 10 条
- 敏感配置统一放 `.env`，用 `python-decouple` 读取
- 所有状态码用 `IntegerChoices` 枚举，禁止硬编码数字

---

## 当前任务

请先完成 **Step 1 + Step 2**，输出：

1. `config/settings/base.py`
2. `utils/response.py`
3. `utils/pagination.py`
4. `apps/users/models.py`
5. `apps/books/models.py`
6. `apps/borrows/models.py`
7. `apps/reservations/models.py`
8. `apps/fines/models.py`
9. `apps/announcements/models.py`
10. `requirements.txt`
