# FastAPI 用户管理系统

这是一个基于 FastAPI、SQLite 和 SQLModel 的用户管理和认证系统。

## 功能特性

- ✅ 用户注册和登录
- ✅ JWT Token 认证
- ✅ 用户信息管理
- ✅ 管理员用户管理功能
- ✅ 密码加密存储（bcrypt自动处理长度限制）
- ✅ SQLite 数据库支持
- ✅ 自动 API 文档
- ✅ 完整的错误处理和数据验证

## 项目结构

```
├── app/
│   ├── __init__.py
│   ├── main.py              # 主应用文件
│   ├── models.py            # 数据模型
│   ├── database.py          # 数据库配置
│   ├── auth.py              # 认证功能
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # 认证路由
│       └── users.py         # 用户管理路由
├── requirements.txt         # Python依赖
├── .env                     # 环境配置
├── run.py                   # 启动脚本
├── start.sh                 # 一键启动脚本
├── test_api.py              # API测试脚本
└── README.md
```

## 快速开始

### 方法 1: 一键启动

```bash
./start.sh
```

### 方法 2: 手动启动

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务器：
```bash
python run.py
```

应用将在 http://localhost:8000 启动

## API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 方法 3: 测试模式

```bash
source .venv/bin/activate
python test_api.py
```

## API 端点

### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取当前用户信息
- `PUT /auth/me` - 更新当前用户信息

### 用户管理（需要管理员权限）
- `GET /users/` - 获取用户列表
- `GET /users/{user_id}` - 获取指定用户
- `PUT /users/{user_id}` - 更新指定用户
- `DELETE /users/{user_id}` - 删除用户
- `POST /users/{user_id}/toggle-active` - 启用/禁用用户

### 系统状态
- `GET /` - 根路径
- `GET /health` - 健康检查

## 初始化管理员用户

1. 注册一个新用户（使用 `/auth/register` 端点）
2. 直接修改数据库，设置 `is_superuser` 为 True：
```sql
UPDATE user SET is_superuser = 1 WHERE username = 'your_username';
```

## 环境配置

在 `.env` 文件中配置：

```env
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
```

## 技术栈

- **后端框架**: FastAPI
- **数据库**: SQLite
- **ORM**: SQLModel
- **认证**: JWT Token
- **密码加密**: bcrypt（自动处理密码长度截断）
- **API文档**: 自动生成