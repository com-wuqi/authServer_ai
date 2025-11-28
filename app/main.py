from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import create_db_and_tables
from .routes import auth, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    create_db_and_tables()
    yield
    # 关闭时的清理操作

app = FastAPI(
    title="用户管理系统API",
    description="基于FastAPI和SQLModel的用户管理与认证系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    """根路径"""
    return {"message": "欢迎使用用户管理系统API"}

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy"}