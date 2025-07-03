from sqlmodel import SQLModel, Field
from typing import Optional
from .base import BaseModel


class Candidate(BaseModel, table=True):
    """候補者モデル"""
    __tablename__ = "candidates"
    
    name: str = Field(description="候補者名")
    email: str = Field(description="メールアドレス", unique=True)
    phone: Optional[str] = Field(default=None, description="電話番号")
    current_company: Optional[str] = Field(default=None, description="現在の勤務先")
    current_position: Optional[str] = Field(default=None, description="現在の職位")
    expected_salary: Optional[int] = Field(default=None, description="希望年収")
    
    def __repr__(self):
        return f"<Candidate(name='{self.name}', email='{self.email}')>" 