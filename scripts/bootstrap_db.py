#!/usr/bin/env python3
"""
データベース初期化スクリプト
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.base import create_tables
from app.models import (
    Candidate, Job, Application, Event, Task, MessageRaw, EmbeddingChunk
)


def main():
    """データベースの初期化"""
    print("📊 データベースの初期化を開始します...")
    
    try:
        # テーブル作成
        create_tables()
        print("✅ 全テーブルが正常に作成されました")
        
        # 作成されたテーブルの確認
        print("\n📋 作成されたテーブル:")
        print("- candidates (候補者)")
        print("- jobs (求人)")
        print("- applications (応募)")
        print("- events (イベント)")
        print("- tasks (タスク)")
        print("- message_raw (メッセージ)")
        print("- embedding_chunks (埋め込みチャンク)")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 