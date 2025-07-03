#!/usr/bin/env python3
"""
サンプルデータ投入スクリプト
"""

import sys
import os
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session
from app.models.base import engine
from app.models import (
    Candidate, Job, Application, Event, Task, MessageRaw
)


def create_sample_data():
    """サンプルデータの作成"""
    print("📊 サンプルデータを作成しています...")
    
    with Session(engine) as session:
        # 候補者データ
        candidates = [
            Candidate(
                name="田中太郎",
                email="tanaka@example.com",
                phone="090-1234-5678",
                current_company="ABC株式会社",
                current_position="エンジニア",
                expected_salary=8000000
            ),
            Candidate(
                name="佐藤花子",
                email="sato@example.com",
                phone="090-9876-5432",
                current_company="XYZ株式会社",
                current_position="マネージャー",
                expected_salary=10000000
            ),
            Candidate(
                name="鈴木一郎",
                email="suzuki@example.com",
                phone="090-1111-2222",
                current_company="DEF株式会社",
                current_position="リーダー",
                expected_salary=7500000
            )
        ]
        
        # 求人データ
        jobs = [
            Job(
                company="Acme株式会社",
                title="シニアエンジニア",
                ra_owner="山田RA",
                description="Pythonを使ったバックエンド開発",
                salary_min=7000000,
                salary_max=12000000,
                location="東京都渋谷区"
            ),
            Job(
                company="Tech Corp",
                title="プロダクトマネージャー",
                ra_owner="佐々木RA",
                description="新規事業のプロダクト開発",
                salary_min=9000000,
                salary_max=15000000,
                location="東京都港区"
            ),
            Job(
                company="StartUp Inc",
                title="フロントエンドエンジニア",
                ra_owner="田中RA",
                description="React/TypeScriptを使った開発",
                salary_min=6000000,
                salary_max=9000000,
                location="東京都新宿区"
            )
        ]
        
        # データベースに保存
        session.add_all(candidates)
        session.add_all(jobs)
        session.commit()
        print("✅ 候補者と求人データを追加しました")
        
        # 応募データ
        applications = [
            Application(
                candidate_id=candidates[0].id,
                job_id=jobs[0].id,
                status="書類選考中",
                latest_summary="技術力は高いが、転職理由を詳しく聞く必要がある",
                enthusiasm_score=0.8,
                concern_score=0.3
            ),
            Application(
                candidate_id=candidates[1].id,
                job_id=jobs[1].id,
                status="面接調整中",
                latest_summary="マネジメント経験豊富、年収交渉が必要",
                enthusiasm_score=0.9,
                concern_score=0.2
            ),
            Application(
                candidate_id=candidates[2].id,
                job_id=jobs[2].id,
                status="内定",
                latest_summary="技術的にはマッチしているが、待遇面で悩んでいる",
                enthusiasm_score=0.7,
                concern_score=0.6
            )
        ]
        
        session.add_all(applications)
        session.commit()
        print("✅ 応募データを追加しました")
        
        # タスクデータ
        now = datetime.now()
        tasks = [
            Task(
                application_id=applications[0].id,
                owner="CA",
                description="CSへ面接候補日を提示",
                due=now + timedelta(days=2),
                priority="high",
                status="open"
            ),
            Task(
                application_id=applications[1].id,
                owner="CA",
                description="候補日をRAに転送",
                due=now + timedelta(days=1),
                priority="medium",
                status="open"
            ),
            Task(
                application_id=applications[2].id,
                owner="CA",
                description="労働条件確認依頼をCSに送付",
                due=now + timedelta(days=3),
                priority="high",
                status="open"
            )
        ]
        
        session.add_all(tasks)
        session.commit()
        print("✅ タスクデータを追加しました")
        
        # サンプルメッセージデータ
        messages = [
            MessageRaw(
                msg_type="email",
                external_id="gmail_msg_001",
                body="田中様、書類選考の結果についてお知らせします。技術力については問題ありませんが、転職理由について詳しくお聞かせください。",
                subject="書類選考結果について",
                sender="ca@example.com",
                recipient="tanaka@example.com"
            ),
            MessageRaw(
                msg_type="transcript",
                external_id="zoom_rec_001",
                body="佐藤さん、本日は面談のお時間をいただきありがとうございました。現在のお仕事での課題や今後のキャリアについてお聞かせください。マネジメント経験は豊富とのことですが、具体的にはどのような...",
                subject="面談記録",
                sender="ca@example.com",
                recipient="sato@example.com"
            )
        ]
        
        session.add_all(messages)
        session.commit()
        print("✅ メッセージデータを追加しました")
        
        print("\n📊 サンプルデータの作成が完了しました！")
        print(f"- 候補者: {len(candidates)}件")
        print(f"- 求人: {len(jobs)}件")
        print(f"- 応募: {len(applications)}件")
        print(f"- タスク: {len(tasks)}件")
        print(f"- メッセージ: {len(messages)}件")


def main():
    """メイン実行関数"""
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 