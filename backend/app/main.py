from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.auth import router as auth_router
from .api.users import router as users_router
from .database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

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
app.include_router(users_router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
