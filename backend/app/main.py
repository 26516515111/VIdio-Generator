import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.auth import router as auth_router
from .api.llm import router as llm_router
from .api.ocr import router as ocr_router
from .api.tts import router as tts_router
from .api.users import router as users_router
from .database import init_db


def get_frontend_dist() -> Path:
    """获取前端构建产物目录，兼容开发环境和 PyInstaller 打包环境"""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent
    return base / "frontend" / "dist"


app = FastAPI(title="语音转换助手")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(llm_router)
app.include_router(ocr_router)
app.include_router(tts_router)
app.include_router(users_router)


# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


# 挂载前端静态资源
frontend_dist = get_frontend_dist()
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """SPA 回退：非 API 路径一律返回 index.html"""
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dist / "index.html"))
