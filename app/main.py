from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, dishes, customer_selections, chef_selections, bindings, binding_requests

app = FastAPI(
    title="Tiny Menu API",
    description="智能点餐系统后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """
    根路径端点，返回API基本信息
    """
    return {
        "message": "欢迎使用 Tiny Menu API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点，用于监控服务状态
    """
    return {
        "status": "healthy",
        "service": "Tiny Menu API"
    }


# 注册路由
app.include_router(auth.router)
app.include_router(dishes.router)
app.include_router(customer_selections.router)
app.include_router(chef_selections.router)
app.include_router(bindings.router)
app.include_router(binding_requests.router)

if __name__ == "__main__":
    import uvicorn
    from .config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
