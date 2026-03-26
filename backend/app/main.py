from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router

app = FastAPI(
    title="标准智能评估系统",
    description="基于大模型的标准条款智能拆解与评估系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "标准智能评估系统 API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
