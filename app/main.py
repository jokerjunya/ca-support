from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from app.core.config import settings
from app.models.base import get_session, create_tables
from app.models import (
    Candidate, Job, Application, Event, Task, MessageRaw, EmbeddingChunk
)

# FastAPIアプリケーションの作成
app = FastAPI(
    title="CA Support System",
    description="キャリアアドバイザー支援システム",
    version="1.0.0",
    debug=settings.debug
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """起動時の初期化処理"""
    print("🚀 CA Support System を起動しています...")
    create_tables()
    print("✅ データベーステーブルを作成しました")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "CA Support System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


# 基本的なCRUD API
@app.get("/api/candidates")
async def get_candidates(session: Session = Depends(get_session)):
    """候補者一覧を取得"""
    candidates = session.query(Candidate).all()
    return candidates


@app.get("/api/jobs")
async def get_jobs(session: Session = Depends(get_session)):
    """求人一覧を取得"""
    jobs = session.query(Job).all()
    return jobs


@app.get("/api/applications")
async def get_applications(session: Session = Depends(get_session)):
    """応募一覧を取得"""
    applications = session.query(Application).all()
    return applications


@app.get("/api/tasks")
async def get_tasks(session: Session = Depends(get_session)):
    """タスク一覧を取得"""
    tasks = session.query(Task).all()
    return tasks


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 