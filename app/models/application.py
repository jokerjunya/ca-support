from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from .base import BaseModel


class Application(BaseModel, table=True):
    """応募モデル"""
    __tablename__ = "applications"
    
    candidate_id: str = Field(foreign_key="candidates.id", description="候補者ID")
    job_id: str = Field(foreign_key="jobs.id", description="求人ID")
    status: str = Field(default="書類選考中", description="応募ステータス")
    latest_summary: Optional[str] = Field(default=None, description="最新要約")
    enthusiasm_score: Optional[float] = Field(default=None, description="熱意スコア (0-1)")
    concern_score: Optional[float] = Field(default=None, description="懸念スコア (0-1)")
    
    def __repr__(self):
        return f"<Application(candidate_id='{self.candidate_id}', job_id='{self.job_id}', status='{self.status}')>" 