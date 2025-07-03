from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel


class Event(BaseModel, table=True):
    """イベントモデル"""
    __tablename__ = "events"
    
    application_id: str = Field(foreign_key="applications.id", description="応募ID")
    event_type: str = Field(description="イベントタイプ")
    happened_at: datetime = Field(description="発生日時")
    summary: str = Field(description="要約 (≤200字)")
    payload: Optional[Dict[str, Any]] = Field(
        default=None, 
        sa_column=Column(JSON), 
        description="追加データ（熱意スコア、懸念スコア等）"
    )
    
    def __repr__(self):
        return f"<Event(type='{self.event_type}', application_id='{self.application_id}')>" 