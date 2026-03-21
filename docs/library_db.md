# 图书角图书管理系统 · 数据库初始化 SQL

```sql
-- ========================================
-- 图书角图书管理系统 · 数据库初始化脚本
-- 技术栈: Django + Vue3
-- 字符集: utf8mb4 | 引擎: InnoDB | MySQL 8.x
-- ========================================

CREATE DATABASE IF NOT EXISTS library_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE library_db;


-- ----------------------------------------
-- 1. 用户表 users
-- role:   0=普通读者  1=管理员  2=超级管理员
-- status: 0=禁用      1=正常
-- ----------------------------------------
CREATE TABLE users (
  id            INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(50)      NOT NULL UNIQUE          COMMENT '登录用户名',
  password_hash VARCHAR(255)     NOT NULL                 COMMENT 'bcrypt 密码哈希',
  real_name     VARCHAR(50)      NOT NULL                 COMMENT '真实姓名',
  email         VARCHAR(100)     UNIQUE                   COMMENT '邮箱',
  phone         VARCHAR(20)                               COMMENT '手机号',
  role          TINYINT UNSIGNED NOT NULL DEFAULT 0       COMMENT '角色: 0=读者 1=管理员 2=超管',
  status        TINYINT UNSIGNED NOT NULL DEFAULT 1       COMMENT '状态: 0=禁用 1=正常',
  avatar_url    VARCHAR(255)                              COMMENT '头像地址',
  created_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_role   (role),
  INDEX idx_status (status)
) COMMENT='用户表';


-- ----------------------------------------
-- 2. 图书分类表 categories（支持树形）
-- ----------------------------------------
CREATE TABLE categories (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(50)  NOT NULL                  COMMENT '分类名称',
  code       VARCHAR(20)  UNIQUE                    COMMENT '分类编号，如 TP312',
  parent_id  INT UNSIGNED DEFAULT NULL              COMMENT '父分类 ID，NULL=根分类',
  sort_order INT UNSIGNED NOT NULL DEFAULT 0        COMMENT '排序权重，越小越靠前',
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
  INDEX idx_parent (parent_id)
) COMMENT='图书分类表（树形）';


-- ----------------------------------------
-- 3. 图书信息表 books（逻辑书）
-- status: 0=下架  1=上架
-- ----------------------------------------
CREATE TABLE books (
  id               INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  isbn             VARCHAR(20)      UNIQUE                    COMMENT 'ISBN 号',
  title            VARCHAR(255)     NOT NULL                  COMMENT '书名',
  author           VARCHAR(255)     NOT NULL                  COMMENT '作者',
  publisher        VARCHAR(100)                               COMMENT '出版社',
  cover_url        VARCHAR(255)                               COMMENT '封面图片地址',
  description      TEXT                                       COMMENT '简介',
  category_id      INT UNSIGNED                               COMMENT '分类 ID',
  total_copies     INT UNSIGNED     NOT NULL DEFAULT 0        COMMENT '馆藏总册数',
  available_copies INT UNSIGNED     NOT NULL DEFAULT 0        COMMENT '当前可借册数（冗余，事务维护）',
  price            DECIMAL(8, 2)                              COMMENT '定价（元）',
  publish_date     DATE                                       COMMENT '出版日期',
  language         VARCHAR(20)      DEFAULT 'zh'              COMMENT '语言',
  status           TINYINT UNSIGNED NOT NULL DEFAULT 1        COMMENT '状态: 0=下架 1=上架',
  created_at       DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
  FULLTEXT INDEX ft_title_author (title, author) WITH PARSER ngram,
  INDEX idx_category (category_id),
  INDEX idx_status   (status)
) COMMENT='图书信息表';


-- ----------------------------------------
-- 4. 图书副本表 book_copies（实体书）
-- condition: 1=全新  2=良好  3=一般  4=破损
-- status:    0=注销  1=在馆  2=借出  3=预约锁定  4=丢失
-- ----------------------------------------
CREATE TABLE book_copies (
  id          INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  book_id     INT UNSIGNED     NOT NULL                  COMMENT '所属图书 ID',
  barcode     VARCHAR(50)      NOT NULL UNIQUE            COMMENT '实体书条形码',
  `condition` TINYINT UNSIGNED NOT NULL DEFAULT 1        COMMENT '品相: 1=全新 2=良好 3=一般 4=破损',
  status      TINYINT UNSIGNED NOT NULL DEFAULT 1        COMMENT '状态: 0=注销 1=在馆 2=借出 3=预约锁 4=丢失',
  location    VARCHAR(50)                                COMMENT '书架位置，如 A区-03-2',
  created_at  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
  INDEX idx_book   (book_id),
  INDEX idx_status (status)
) COMMENT='图书副本表（实体书）';


-- ----------------------------------------
-- 5. 借阅记录表 borrows
-- status: 0=已还  1=借阅中  2=逾期  3=丢失
-- ----------------------------------------
CREATE TABLE borrows (
  id           INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  user_id      INT UNSIGNED     NOT NULL               COMMENT '借阅用户',
  book_copy_id INT UNSIGNED     NOT NULL               COMMENT '借出的实体书',
  book_id      INT UNSIGNED     NOT NULL               COMMENT '冗余图书 ID，方便统计查询',
  borrow_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '借出时间',
  due_at       DATETIME         NOT NULL               COMMENT '应还时间',
  return_at    DATETIME         DEFAULT NULL            COMMENT '实际归还时间',
  status       TINYINT UNSIGNED NOT NULL DEFAULT 1     COMMENT '状态: 0=已还 1=借阅中 2=逾期 3=丢失',
  operator_id  INT UNSIGNED     DEFAULT NULL            COMMENT '经手管理员 ID',
  remark       TEXT                                    COMMENT '备注',
  FOREIGN KEY (user_id)      REFERENCES users(id),
  FOREIGN KEY (book_copy_id) REFERENCES book_copies(id),
  FOREIGN KEY (book_id)      REFERENCES books(id),
  FOREIGN KEY (operator_id)  REFERENCES users(id),
  INDEX idx_user   (user_id),
  INDEX idx_copy   (book_copy_id),
  INDEX idx_book   (book_id),
  INDEX idx_status (status),
  INDEX idx_due    (due_at)       -- 定时扫描逾期关键索引
) COMMENT='借阅记录表';


-- ----------------------------------------
-- 6. 续借记录表 renewals
-- ----------------------------------------
CREATE TABLE renewals (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  borrow_id  INT UNSIGNED NOT NULL               COMMENT '对应借阅记录',
  renewed_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '续借时间',
  new_due_at DATETIME     NOT NULL               COMMENT '续借后应还时间',
  FOREIGN KEY (borrow_id) REFERENCES borrows(id) ON DELETE CASCADE,
  INDEX idx_borrow (borrow_id)
) COMMENT='续借记录表';


-- ----------------------------------------
-- 7. 预约记录表 reservations
-- status: 0=已取消  1=预约中  2=已到馆  3=已完成  4=已过期
-- ----------------------------------------
CREATE TABLE reservations (
  id          INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  user_id     INT UNSIGNED     NOT NULL               COMMENT '预约用户',
  book_id     INT UNSIGNED     NOT NULL               COMMENT '预约图书（逻辑书）',
  status      TINYINT UNSIGNED NOT NULL DEFAULT 1     COMMENT '状态: 0=取消 1=等待 2=到馆 3=完成 4=过期',
  reserved_at DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '预约时间',
  expire_at   DATETIME         NOT NULL               COMMENT '预约到期时间',
  notify_at   DATETIME         DEFAULT NULL            COMMENT '到馆通知时间',
  cancel_at   DATETIME         DEFAULT NULL            COMMENT '取消时间',
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (book_id) REFERENCES books(id),
  INDEX idx_user   (user_id),
  INDEX idx_book   (book_id),
  INDEX idx_status (status)
) COMMENT='图书预约记录表';


-- ----------------------------------------
-- 8. 罚款记录表 fines
-- status: 0=待缴  1=已缴  2=已免除
-- ----------------------------------------
CREATE TABLE fines (
  id         INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  borrow_id  INT UNSIGNED     NOT NULL               COMMENT '关联借阅记录',
  user_id    INT UNSIGNED     NOT NULL               COMMENT '欠款用户',
  amount     DECIMAL(8, 2)    NOT NULL               COMMENT '罚款金额（元）',
  reason     VARCHAR(100)     DEFAULT '逾期还书'      COMMENT '原因',
  status     TINYINT UNSIGNED NOT NULL DEFAULT 0     COMMENT '状态: 0=待缴 1=已缴 2=免除',
  created_at DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  paid_at    DATETIME         DEFAULT NULL            COMMENT '缴清时间',
  FOREIGN KEY (borrow_id) REFERENCES borrows(id),
  FOREIGN KEY (user_id)   REFERENCES users(id),
  INDEX idx_user   (user_id),
  INDEX idx_status (status)
) COMMENT='罚款记录表';


-- ----------------------------------------
-- 9. 公告表 announcements
-- status: 0=草稿  1=已发布  2=已下架
-- ----------------------------------------
CREATE TABLE announcements (
  id           INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  admin_id     INT UNSIGNED     NOT NULL               COMMENT '发布管理员',
  title        VARCHAR(100)     NOT NULL               COMMENT '标题',
  content      TEXT             NOT NULL               COMMENT '内容（支持 HTML）',
  status       TINYINT UNSIGNED NOT NULL DEFAULT 0     COMMENT '状态: 0=草稿 1=发布 2=下架',
  published_at DATETIME         DEFAULT NULL            COMMENT '发布时间',
  created_at   DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (admin_id) REFERENCES users(id),
  INDEX idx_status (status)
) COMMENT='公告表';


-- ========================================
-- 初始化数据
-- ========================================

-- 超级管理员（密码明文: admin123，部署前请替换为真实 bcrypt 哈希）
INSERT INTO users (username, password_hash, real_name, role, status)
VALUES ('admin', '$2b$12$exampleHashHereXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', '系统管理员', 2, 1);

-- 根分类
INSERT INTO categories (name, code, parent_id, sort_order) VALUES
  ('文学',     'I',  NULL, 1),
  ('计算机',   'TP', NULL, 2),
  ('历史',     'K',  NULL, 3),
  ('自然科学', 'N',  NULL, 4);

-- 计算机子分类示例
INSERT INTO categories (name, code, parent_id, sort_order) VALUES
  ('程序设计', 'TP312', 2, 1),
  ('数据库',   'TP311', 2, 2),
  ('网络',     'TP393', 2, 3);
```
