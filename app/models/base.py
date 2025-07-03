from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime
import uuid


def generate_id() -> str:
    """UUIDを生成する"""
    return str(uuid.uuid4())


class BaseModel(SQLModel):
    """全テーブルの基底クラス"""
    id: str = Field(default_factory=generate_id, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# SQLiteデータベース設定（開発用）
DATABASE_URL = "sqlite:///./ca_support.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """データベースセッションを取得"""
    with Session(engine) as session:
        yield session


def create_tables():
    """全テーブルを作成"""
    SQLModel.metadata.create_all(engine) 