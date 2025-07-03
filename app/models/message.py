from sqlmodel import SQLModel, Field, Column
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseModel


class MessageRaw(BaseModel, table=True):
    """生メッセージモデル"""
    __tablename__ = "message_raw"
    
    msg_type: str = Field(description="メッセージタイプ (email, transcript)")
    external_id: str = Field(description="外部ID (Gmail ID, 録画ID等)", unique=True)
    body: str = Field(description="メッセージ本文")
    subject: Optional[str] = Field(default=None, description="件名")
    sender: Optional[str] = Field(default=None, description="送信者")
    recipient: Optional[str] = Field(default=None, description="受信者")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="メタデータ")
    
    def __repr__(self):
        return f"<MessageRaw(type='{self.msg_type}', external_id='{self.external_id}')>"


class EmbeddingChunk(BaseModel, table=True):
    """埋め込みチャンクモデル"""
    __tablename__ = "embedding_chunks"
    
    message_id: str = Field(foreign_key="message_raw.id", description="メッセージID")
    chunk_index: int = Field(description="チャンクインデックス")
    text: str = Field(description="チャンクテキスト")
    vector: Optional[List[float]] = Field(default=None, description="埋め込みベクトル")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="メタデータ")
    
    def __repr__(self):
        return f"<EmbeddingChunk(message_id='{self.message_id}', chunk_index={self.chunk_index})>" 