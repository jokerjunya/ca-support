#!/usr/bin/env python3
"""
メール生成デバッグスクリプト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.llm import EmailGenerationContext, QwenLLM

def test_actual_generation():
    """実際のメール生成処理をテスト"""
    
    # 実際のアプリケーションと同じコンテキストを作成
    context = EmailGenerationContext(
        candidate_name="田中太郎",
        company="Acme株式会社",
        job_title="シニアエンジニア",
        status="書類選考中",
        latest_summary="技術力は高いが、転職理由を詳しく聞く必要がある。現在の年収が700万円で、希望が800万円なので条件面は問題なし。",
        enthusiasm_score=0.8,
        concern_score=0.3,
        target_person="CS",
        current_template="田中太郎様の面接候補日をお送りします。以下の日程でご調整いただけますでしょうか。\n\n候補日：\n- {date1}\n- {date2}\n- {date3}"
    )
    
    # QwenLLMインスタンスを作成
    llm = QwenLLM()
    
    print("=== 実際のメール生成処理をテスト ===")
    print(f"候補者: {context.candidate_name}")
    print(f"企業: {context.company}")
    print(f"職種: {context.job_title}")
    print(f"対象者: {context.target_person}")
    print()
    
    # メール生成を実行
    result = llm.generate_email_content(context)
    
    print("=== 生成結果 ===")
    print(f"件名: {result['subject']}")
    print(f"本文: {result['body']}")
    print(f"メタデータ: {result['metadata']}")
    print()
    
    # 生のレスポンスも確認
    if 'raw_response' in result:
        print("=== 生レスポンス ===")
        print(result['raw_response'])
    
    return result

if __name__ == "__main__":
    test_actual_generation() 