from sqlmodel import SQLModel, Field
from typing import Optional
from .base import BaseModel


class Job(BaseModel, table=True):
    """求人モデル"""
    __tablename__ = "jobs"
    
    company: str = Field(description="企業名")
    title: str = Field(description="職種・ポジション")
    ra_owner: str = Field(description="担当RA（リクルーティングアドバイザー）")
    description: Optional[str] = Field(default=None, description="求人詳細")
    salary_min: Optional[int] = Field(default=None, description="最低年収")
    salary_max: Optional[int] = Field(default=None, description="最高年収")
    location: Optional[str] = Field(default=None, description="勤務地")
    status: str = Field(default="active", description="求人ステータス")
    
    def __repr__(self):
        return f"<Job(company='{self.company}', title='{self.title}')>" 