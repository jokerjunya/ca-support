from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseModel


class Task(BaseModel, table=True):
    """タスクモデル"""
    __tablename__ = "tasks"
    
    application_id: str = Field(foreign_key="applications.id", description="応募ID")
    owner: str = Field(description="担当者 (CA, RA, CS等)")
    description: str = Field(description="タスク内容")
    due: datetime = Field(description="期限")
    priority: str = Field(default="medium", description="優先度 (low, medium, high)")
    status: str = Field(default="open", description="ステータス (open, in_progress, completed)")
    
    def __repr__(self):
        return f"<Task(owner='{self.owner}', description='{self.description[:30]}...')>" 