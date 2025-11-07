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

# 注册路由
app.include_router(auth.router)
app.include_router(dishes.router)
app.include_router(customer_selections.router)
app.include_router(chef_selections.router)
app.include_router(bindings.router)
app.include_router(binding_requests.router)

@app.get("/")
def root():
    """健康检查"""
    return {
        "message": "Tiny Menu API is running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from .config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
