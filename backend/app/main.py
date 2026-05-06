from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.auth import router as auth_router
from .api.llm import router as llm_router
from .api.users import router as users_router
from .database import init_db

app = FastAPI(title="语音转换助手")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(llm_router)
app.include_router(users_router)


# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
