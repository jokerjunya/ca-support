#!/usr/bin/env python3
"""
CA Support System - デモ版 API
データベースを使わずにメモリ上のサンプルデータで動作する簡易版
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json
from app.core.llm import llm, EmailGenerationContext
from app.core.template_engine import TemplateEngine, StatusContext, TemplateRecommendation

# FastAPIアプリケーション
app = FastAPI(
    title="CA Support System - デモ版",
    description="キャリアアドバイザー支援システムのデモ版",
    version="0.1.0"
)

# テンプレートエンジンのインスタンス作成
template_engine = TemplateEngine()

# データモデル（簡易版）
class Candidate(BaseModel):
    id: str
    name: str
    email: str
    current_company: str
    expected_salary: int

class Job(BaseModel):
    id: str
    company: str
    title: str
    ra_owner: str
    salary_range: str

class Application(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    status: str
    latest_summary: str
    enthusiasm_score: float
    concern_score: float
    candidate_name: str
    job_title: str
    company: str

class Task(BaseModel):
    id: str
    application_id: str
    owner: str
    description: str
    due: str
    priority: str
    status: str
    candidate_name: str
    company: str

class NextAction(BaseModel):
    id: str
    application_id: str
    action_type: str  # "send_email", "schedule_call", "update_status"
    target_person: str  # "CS", "candidate", "RA"
    target_email: str
    subject: str
    message_template: str
    priority: str
    due_date: str

class MessageHistory(BaseModel):
    id: str
    application_id: str
    timestamp: str
    message_type: str  # "email_sent", "email_received", "interview", "note"
    sender: str
    receiver: str
    subject: str
    content: str
    is_outbound: bool

# サンプルデータ
sample_candidates = [
    Candidate(
        id="cand_001",
        name="田中太郎",
        email="tanaka@example.com",
        current_company="ABC株式会社",
        expected_salary=8000000
    ),
    Candidate(
        id="cand_002",
        name="佐藤花子",
        email="sato@example.com",
        current_company="XYZ株式会社",
        expected_salary=10000000
    ),
    Candidate(
        id="cand_003",
        name="鈴木一郎",
        email="suzuki@example.com",
        current_company="DEF株式会社",
        expected_salary=7500000
    )
]

sample_jobs = [
    Job(
        id="job_001",
        company="Acme株式会社",
        title="シニアエンジニア",
        ra_owner="山田RA",
        salary_range="700-1200万円"
    ),
    Job(
        id="job_002",
        company="Tech Corp",
        title="プロダクトマネージャー",
        ra_owner="佐々木RA",
        salary_range="900-1500万円"
    ),
    Job(
        id="job_003",
        company="StartUp Inc",
        title="フロントエンドエンジニア",
        ra_owner="田中RA",
        salary_range="600-900万円"
    )
]

sample_applications = [
    Application(
        id="app_001",
        candidate_id="cand_001",
        job_id="job_001",
        status="書類選考中",
        latest_summary="技術力は高いが、転職理由を詳しく聞く必要がある。現在の年収が700万円で、希望が800万円なので条件面は問題なし。",
        enthusiasm_score=0.8,
        concern_score=0.3,
        candidate_name="田中太郎",
        job_title="シニアエンジニア",
        company="Acme株式会社"
    ),
    Application(
        id="app_002",
        candidate_id="cand_002",
        job_id="job_002",
        status="面接調整中",
        latest_summary="マネジメント経験豊富で即戦力として期待。年収交渉が必要だが、企業側も前向き。面接日程の調整を急ぐ。",
        enthusiasm_score=0.9,
        concern_score=0.2,
        candidate_name="佐藤花子",
        job_title="プロダクトマネージャー",
        company="Tech Corp"
    ),
    Application(
        id="app_003",
        candidate_id="cand_003",
        job_id="job_003",
        status="内定",
        latest_summary="技術的にはマッチしているが、給与面で悩んでいる様子。スタートアップの将来性に不安を感じている。",
        enthusiasm_score=0.7,
        concern_score=0.6,
        candidate_name="鈴木一郎",
        job_title="フロントエンドエンジニア",
        company="StartUp Inc"
    )
]

now = datetime.now()
sample_tasks = [
    Task(
        id="task_001",
        application_id="app_001",
        owner="CA",
        description="CSへ面接候補日を提示",
        due=(now + timedelta(days=2)).strftime("%Y-%m-%d"),
        priority="high",
        status="open",
        candidate_name="田中太郎",
        company="Acme株式会社"
    ),
    Task(
        id="task_002",
        application_id="app_002",
        owner="CA",
        description="候補日をRAに転送",
        due=(now + timedelta(days=1)).strftime("%Y-%m-%d"),
        priority="medium",
        status="open",
        candidate_name="佐藤花子",
        company="Tech Corp"
    ),
    Task(
        id="task_003",
        application_id="app_003",
        owner="CA",
        description="労働条件確認依頼をCSに送付",
        due=(now + timedelta(days=3)).strftime("%Y-%m-%d"),
        priority="high",
        status="open",
        candidate_name="鈴木一郎",
        company="StartUp Inc"
    ),
    Task(
        id="task_004",
        application_id="app_003",
        owner="CA",
        description="給与条件の再交渉",
        due=(now + timedelta(days=1)).strftime("%Y-%m-%d"),
        priority="high",
        status="open",
        candidate_name="鈴木一郎",
        company="StartUp Inc"
    )
]

# ネクストアクション（将来LLM統合用）
sample_next_actions = [
    NextAction(
        id="action_001",
        application_id="app_001",
        action_type="send_email",
        target_person="CS",
        target_email="cs@acme.com",
        subject="面接候補日の提示について（田中太郎様）",
        message_template="田中太郎様の面接候補日をお送りします。以下の日程でご調整いただけますでしょうか。\n\n候補日：\n- {date1}\n- {date2}\n- {date3}",
        priority="high",
        due_date=(now + timedelta(days=2)).strftime("%Y-%m-%d")
    ),
    NextAction(
        id="action_002",
        application_id="app_002",
        action_type="send_email",
        target_person="candidate",
        target_email="sato@example.com",
        subject="面接準備について（Tech Corp様）",
        message_template="佐藤様、Tech Corp様との面接に向けた準備資料をお送りいたします。想定質問と企業情報をご確認ください。",
        priority="high",
        due_date=(now + timedelta(days=1)).strftime("%Y-%m-%d")
    ),
    NextAction(
        id="action_003",
        application_id="app_003",
        action_type="send_email",
        target_person="candidate",
        target_email="suzuki@example.com",
        subject="労働条件について（StartUp Inc様）",
        message_template="鈴木様、お疲れ様です。StartUp Inc様の労働条件について追加でご相談があります。{details}",
        priority="high",
        due_date=(now + timedelta(days=1)).strftime("%Y-%m-%d")
    )
]

# メッセージ履歴（統合されたリアルなデータ）
from complete_integrated_history import all_message_history

# API エンドポイント
@app.get("/")
async def root():
    """ルートページ - システム情報を表示"""
    return {
        "system": "CA Support System - デモ版",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "dashboard": "/dashboard",
            "applications": "/api/applications",
            "application_detail": "/application/{application_id}",
            "tasks": "/api/tasks",
            "candidates": "/api/candidates",
            "jobs": "/api/jobs"
        }
    }

@app.get("/api/applications", response_model=List[Application])
async def get_applications():
    """応募一覧を取得"""
    return sample_applications

@app.get("/api/applications/{application_id}")
async def get_application_detail(application_id: str):
    """特定の応募の詳細を取得"""
    app = next((a for a in sample_applications if a.id == application_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # 関連データを取得
    next_action = next((a for a in sample_next_actions if a.application_id == application_id), None)
    messages = [m for m in all_message_history if m.application_id == application_id]
    messages.sort(key=lambda x: x.timestamp)
    
    return {
        "application": app,
        "next_action": next_action,
        "message_history": messages
    }

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    """タスク一覧を取得"""
    return sample_tasks

@app.get("/api/candidates", response_model=List[Candidate])
async def get_candidates():
    """候補者一覧を取得"""
    return sample_candidates

@app.get("/api/jobs", response_model=List[Job])
async def get_jobs():
    """求人一覧を取得"""
    return sample_jobs

@app.post("/api/generate-email/{application_id}")
async def generate_email(application_id: str):
    """AI文面生成API"""
    # 対象の応募を取得
    app = next((a for a in sample_applications if a.id == application_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # 対応するネクストアクションを取得
    next_action = next((a for a in sample_next_actions if a.application_id == application_id), None)
    if not next_action:
        raise HTTPException(status_code=404, detail="Next action not found")
    
    # 関連するメッセージ履歴を取得
    messages = [m for m in all_message_history if m.application_id == application_id]
    
    # 履歴を時系列で整理
    messages.sort(key=lambda x: x.timestamp)
    
    # 履歴サマリーを作成
    history_context = ""
    if messages:
        history_context = "\n\n## 過去のやり取り履歴\n"
        for msg in messages[-3:]:  # 最新3件を使用
            direction = "送信" if msg.is_outbound else "受信"
            history_context += f"""
### {msg.timestamp} - {direction}
**{msg.sender} → {msg.receiver}**
件名: {msg.subject}
内容: {msg.content}
"""
    
    # LLM用のコンテキストを作成（履歴情報を含む）
    context = EmailGenerationContext(
        candidate_name=app.candidate_name,
        company=app.company,
        job_title=app.job_title,
        status=app.status,
        latest_summary=app.latest_summary + history_context,  # 履歴を追加
        enthusiasm_score=app.enthusiasm_score,
        concern_score=app.concern_score,
        target_person=next_action.target_person,
        current_template=next_action.message_template
    )
    
    # AI文面生成
    try:
        result = llm.generate_email_content(context)
        return {
            "success": True,
            "generated_subject": result["subject"],
            "generated_body": result["body"],
            "metadata": result.get("metadata", {}),
            "original_template": next_action.message_template,
            "context_used": f"履歴{len(messages)}件を含む詳細コンテキスト"
        }
    except Exception as e:
        print(f"[ERROR] AI文面生成でエラー: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "generated_subject": next_action.subject,
            "generated_body": next_action.message_template
        }

@app.post("/api/analyze-email")
async def analyze_email(email_data: dict):
    """メール内容分析API"""
    content = email_data.get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="Email content is required")
    
    try:
        result = llm.analyze_email_content(content)
        return {
            "success": True,
            "enthusiasm_score": result["enthusiasm_score"],
            "concern_score": result["concern_score"],
            "analysis_reason": result["analysis_reason"],
            "raw_response": result.get("raw_response", "")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "enthusiasm_score": 0.5,
            "concern_score": 0.5,
            "analysis_reason": "分析に失敗しました"
        }

@app.post("/api/test-llm")
async def test_llm():
    """LLMテスト用API"""
    try:
        result = llm._call_ollama("こんにちは、簡単な挨拶をお願いします。", temperature=0.5, max_tokens=100)
        return {
            "success": True,
            "response": result,
            "test": "simple_greeting"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test": "simple_greeting"
        }

@app.get("/api/template-recommendations/{application_id}")
async def get_template_recommendations(application_id: str):
    """テンプレート推奨API"""
    # 対象の応募を取得
    app = next((a for a in sample_applications if a.id == application_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # メッセージ履歴を取得
    messages = [m for m in all_message_history if m.application_id == application_id]
    message_history = [
        {
            "timestamp": m.timestamp,
            "subject": m.subject,
            "content": m.content,
            "is_outbound": m.is_outbound
        }
        for m in messages
    ]
    
    # ステータスコンテキストを作成
    context = StatusContext(
        current_status=app.status,
        candidate_name=app.candidate_name,
        company=app.company,
        job_title=app.job_title,
        enthusiasm_score=app.enthusiasm_score,
        concern_score=app.concern_score,
        latest_summary=app.latest_summary,
        message_history=message_history
    )
    
    # テンプレート推奨を取得
    try:
        recommendations = template_engine.recommend_templates(context)
        
        # 結果を整形
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                "template_name": rec.template_name,
                "template_content": rec.template_content,
                "relevance_score": rec.relevance_score,
                "reason": rec.reason,
                "sender": rec.sender,
                "receiver": rec.receiver,
                "template_type": rec.template_type.value,
                "customization_hints": rec.customization_hints
            })
        
        return {
            "success": True,
            "application_id": application_id,
            "candidate_name": app.candidate_name,
            "current_status": app.status,
            "recommendations": formatted_recommendations,
            "total_recommendations": len(formatted_recommendations)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "application_id": application_id
        }

@app.post("/api/generate-email-with-template/{application_id}")
async def generate_email_with_template(application_id: str, request_data: dict):
    """テンプレートを参考にしたメール生成API"""
    # 対象の応募を取得
    app = next((a for a in sample_applications if a.id == application_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # 対応するネクストアクションを取得
    next_action = next((a for a in sample_next_actions if a.application_id == application_id), None)
    if not next_action:
        raise HTTPException(status_code=404, detail="Next action not found")
    
    # 関連するメッセージ履歴を取得
    messages = [m for m in all_message_history if m.application_id == application_id]
    messages.sort(key=lambda x: x.timestamp)
    
    # 履歴サマリーを作成
    history_context = ""
    if messages:
        history_context = "\n\n## 過去のやり取り履歴\n"
        for msg in messages[-3:]:  # 最新3件を使用
            direction = "送信" if msg.is_outbound else "受信"
            history_context += f"""
### {msg.timestamp} - {direction}
**{msg.sender} → {msg.receiver}**
件名: {msg.subject}
内容: {msg.content}
"""
    
    # テンプレート情報を取得
    template_name = request_data.get("template_name")
    reference_template = request_data.get("reference_template")
    
    # LLM用のコンテキストを作成
    context = EmailGenerationContext(
        candidate_name=app.candidate_name,
        company=app.company,
        job_title=app.job_title,
        status=app.status,
        latest_summary=app.latest_summary + history_context,
        enthusiasm_score=app.enthusiasm_score,
        concern_score=app.concern_score,
        target_person=next_action.target_person,
        current_template=next_action.message_template,
        reference_template=reference_template,
        template_name=template_name
    )
    
    # AI文面生成
    try:
        result = llm.generate_email_content(context)
        return {
            "success": True,
            "generated_subject": result["subject"],
            "generated_body": result["body"],
            "metadata": result.get("metadata", {}),
            "original_template": next_action.message_template,
            "reference_template": reference_template,
            "template_name": template_name,
            "context_used": f"テンプレート「{template_name}」を参考に、履歴{len(messages)}件を含む詳細コンテキストで生成"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_subject": next_action.subject,
            "generated_body": next_action.message_template,
            "template_name": template_name
        }

@app.get("/application/{application_id}", response_class=HTMLResponse)
async def application_detail_page(application_id: str):
    """案件詳細画面"""
    # データ取得
    app = next((a for a in sample_applications if a.id == application_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    next_action = next((a for a in sample_next_actions if a.application_id == application_id), None)
    messages = [m for m in all_message_history if m.application_id == application_id]
    messages.sort(key=lambda x: x.timestamp, reverse=True)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>案件詳細 - {app.candidate_name} × {app.company}</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .breadcrumb {{ margin-bottom: 20px; color: #666; }}
            .breadcrumb a {{ color: #667eea; text-decoration: none; }}
            .header {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .header h1 {{ margin: 0 0 10px 0; color: #333; }}
            .header .status {{ padding: 8px 16px; border-radius: 20px; font-size: 0.9em; font-weight: bold; color: white; display: inline-block; }}
            .status.reviewing {{ background-color: #ff9800; }}
            .status.interviewing {{ background-color: #2196f3; }}
            .status.offered {{ background-color: #4caf50; }}
            .scores {{ margin-top: 15px; }}
            .score {{ display: inline-block; margin-right: 20px; }}
            .score-label {{ color: #666; font-size: 0.9em; }}
            .score-value {{ font-weight: bold; color: #667eea; font-size: 1.1em; }}
            .next-action {{ background: #f8f9fa; border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .next-action h3 {{ margin: 0 0 10px 0; color: #dc3545; }}
            .action-details {{ background: white; padding: 15px; border-radius: 8px; margin-top: 10px; }}
            .action-meta {{ color: #666; font-size: 0.9em; margin-top: 10px; }}
            .email-template {{ background: #f8f9fa; padding: 15px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; margin-top: 10px; }}
            .send-button {{ background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }}
            .send-button:hover {{ background: #5a6fd8; }}
            .timeline {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: none; }}
            .timeline h2 {{ margin-top: 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            .timeline-item {{ padding: 15px 0; border-bottom: 1px solid #eee; min-width: 800px; }}
            .timeline-item:last-child {{ border-bottom: none; }}
            .timeline-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 8px; }}
            .timeline-time {{ color: #666; font-size: 0.9em; }}
            .timeline-type {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-left: 10px; }}
            .type-email-sent {{ background: #e3f2fd; color: #1976d2; }}
            .type-email-received {{ background: #f3e5f5; color: #7b1fa2; }}
            .type-interview {{ background: #e8f5e8; color: #388e3c; }}
            .type-note {{ background: #fff3e0; color: #f57c00; }}
            .type-internal-note {{ background: #f0f4f8; color: #2d3748; border: 1px solid #cbd5e0; }}
            .timeline-content {{ color: #333; line-height: 1.5; white-space: pre-wrap; word-break: normal; overflow-wrap: anywhere; word-spacing: normal; }}
            .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }}
            .modal-content {{ background-color: white; margin: 5% auto; padding: 30px; border-radius: 10px; width: 80%; max-width: 800px; max-height: 80%; overflow-y: auto; }}
            .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            .modal-header h3 {{ margin: 0; color: #333; }}
            .close {{ color: #999; font-size: 24px; cursor: pointer; }}
            .close:hover {{ color: #333; }}
            .ai-result {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0; }}
            .ai-result h4 {{ margin: 0 0 10px 0; color: #333; }}
            .ai-content {{ background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; white-space: pre-wrap; font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; }}
            .copy-button {{ background: #28a745; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; margin-top: 10px; }}
            .copy-button:hover {{ background: #218838; }}
            .loading-spinner {{ text-align: center; padding: 40px; }}
            .spinner {{ border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 0 auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .template-recommendation {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; margin: 10px 0; padding: 15px; }}
            .template-recommendation:hover {{ background: #e9ecef; cursor: pointer; }}
            .template-recommendation.selected {{ border-color: #667eea; background: #e3f2fd; }}
            .template-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
            .template-name {{ font-weight: bold; color: #333; }}
            .template-score {{ background: #667eea; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
            .template-reason {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
            .template-content {{ background: white; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 0.85em; max-height: 150px; overflow-y: auto; }}
            .template-meta {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.8em; color: #666; }}
            .use-template-button {{ background: #28a745; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9em; }}
            .use-template-button:hover {{ background: #218838; }}
            .template-hints {{ margin-top: 10px; padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; }}
            .template-hints h5 {{ margin: 0 0 5px 0; color: #856404; }}
            .template-hints ul {{ margin: 0; padding-left: 20px; color: #856404; font-size: 0.85em; }}
            .message-length {{ font-size: 0.8em; color: #999; margin-left: 10px; }}
            .expand-controls {{ margin-top: 10px; text-align: left; }}
            .expand-button, .collapse-button {{ background: #667eea; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em; transition: all 0.3s ease; }}
            .expand-button:hover, .collapse-button:hover {{ background: #5a6fd8; transform: translateY(-1px); }}
            .timeline-content {{ transition: max-height 0.4s ease-out, opacity 0.3s ease; overflow: hidden; }}
            .timeline-content.expanding {{ max-height: 2000px; opacity: 1; }}
            .timeline-content.collapsing {{ max-height: 0; opacity: 0; }}
            .timeline-header-controls {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .timeline-controls {{ display: flex; gap: 10px; }}
            .timeline-controls .expand-button, .timeline-controls .collapse-button {{ padding: 8px 16px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="breadcrumb">
                <a href="/dashboard">📊 ダッシュボード</a> / 案件詳細
            </div>
            
            <div class="header">
                <h1>👤 {app.candidate_name} → 🏢 {app.company}</h1>
                <div>
                    <span class="status {'reviewing' if '書類' in app.status else 'interviewing' if '面接' in app.status else 'offered'}">{app.status}</span>
                    <span style="margin-left: 15px; color: #666;">{app.job_title}</span>
                </div>
                <div class="scores">
                    <div class="score">
                        <div class="score-label">熱意スコア</div>
                        <div class="score-value">{int(app.enthusiasm_score * 100)}%</div>
                    </div>
                    <div class="score">
                        <div class="score-label">懸念スコア</div>
                        <div class="score-value">{int(app.concern_score * 100)}%</div>
                    </div>
                </div>
                <div style="margin-top: 15px; color: #666; line-height: 1.5;">
                    {app.latest_summary}
                </div>
            </div>
            
            {f'''
            <div class="next-action">
                <h3>🔴 ネクストアクション</h3>
                <div class="action-details">
                    <strong>{next_action.target_person}へのメール送信</strong>
                    <div class="action-meta">
                        宛先: {next_action.target_email} | 期限: {next_action.due_date} | 優先度: {next_action.priority.upper()}
                    </div>
                    <div style="margin-top: 10px;">
                        <strong>件名:</strong> {next_action.subject}
                    </div>
                    <div class="email-template">{next_action.message_template}</div>
                    <div style="margin-top: 15px;">
                                                 <button class="send-button" onclick="alert('メール送信機能は開発中です（将来LLM統合予定）')">
                             📧 メールを送信
                         </button>
                         <button class="send-button" style="background: #6c757d; margin-left: 10px;" onclick="generateAIEmail('{application_id}')">
                             🤖 AI文面生成
                         </button>
                         <button class="send-button" style="background: #28a745; margin-left: 10px;" onclick="showTemplateRecommendations('{application_id}')">
                             📝 テンプレート提案
                         </button>
                    </div>
                </div>
            </div>
            ''' if next_action else ''}
            
            <div class="timeline">
                <div class="timeline-header-controls">
                    <h2>📜 履歴タイムライン</h2>
                    <div class="timeline-controls">
                        <button class="expand-button" onclick="expandAllMessages()">
                            📖 全て展開
                        </button>
                        <button class="collapse-button" onclick="collapseAllMessages()">
                            📝 全て折り畳み
                        </button>
                    </div>
                </div>
                {generate_timeline_html(messages)}
            </div>
        </div>
        
        <!-- AI文面生成モーダル -->
        <div id="aiModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>🤖 AI文面生成</h3>
                    <span class="close" onclick="closeAIModal()">&times;</span>
                </div>
                <div id="aiModalBody">
                    <!-- 動的にコンテンツが挿入される -->
                </div>
            </div>
        </div>
        
        <script>
            // テンプレート推奨表示
            async function showTemplateRecommendations(applicationId) {{
                const modal = document.getElementById('aiModal');
                const modalBody = document.getElementById('aiModalBody');
                
                // モーダルを表示
                modal.style.display = 'block';
                
                // ローディング表示
                modalBody.innerHTML = `
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <p>適切なテンプレートを検索中...</p>
                    </div>
                `;
                
                try {{
                    const response = await fetch(`/api/template-recommendations/${{applicationId}}`);
                    const result = await response.json();
                    
                    if (result.success && result.recommendations.length > 0) {{
                        let recommendationsHtml = `
                            <h4>📝 推奨テンプレート (${{result.recommendations.length}}件)</h4>
                            <p>現在のステータス「${{result.current_status}}」に適したテンプレートを提案します。</p>
                        `;
                        
                        result.recommendations.forEach((rec, index) => {{
                            recommendationsHtml += `
                                <div class="template-recommendation" onclick="selectTemplate(this, '${{rec.template_name}}', '${{rec.template_content}}', '${{applicationId}}')">
                                    <div class="template-header">
                                        <span class="template-name">${{rec.template_name}}</span>
                                        <span class="template-score">${{Math.round(rec.relevance_score * 100)}}%</span>
                                    </div>
                                    <div class="template-reason">${{rec.reason}}</div>
                                    <div class="template-content">${{rec.template_content.substring(0, 200)}}...</div>
                                    <div class="template-meta">
                                        <span>${{rec.sender}} → ${{rec.receiver}}</span>
                                        <span>${{rec.template_type}}</span>
                                    </div>
                                    <div class="template-hints">
                                        <h5>💡 カスタマイズヒント:</h5>
                                        <ul>
                                            ${{rec.customization_hints.map(hint => `<li>${{hint}}</li>`).join('')}}
                                        </ul>
                                    </div>
                                    <button class="use-template-button" onclick="event.stopPropagation(); generateEmailWithTemplate('${{applicationId}}', '${{rec.template_name}}', '${{rec.template_content}}')">
                                        このテンプレートを使用
                                    </button>
                                </div>
                            `;
                        }});
                        
                        modalBody.innerHTML = recommendationsHtml;
                    }} else {{
                        modalBody.innerHTML = `
                            <div class="ai-result">
                                <h4>😔 テンプレートが見つかりませんでした</h4>
                                <p>現在のステータス「${{result.current_status}}」に適したテンプレートが見つかりませんでした。</p>
                                <p>通常のAI文面生成をお試しください。</p>
                                <button class="copy-button" onclick="generateAIEmail('${{applicationId}}')">AI文面生成を実行</button>
                            </div>
                        `;
                    }}
                }} catch (error) {{
                    modalBody.innerHTML = `
                        <div class="ai-result">
                            <h4>❌ エラーが発生しました</h4>
                            <p>テンプレート取得に失敗しました: ${{error.message}}</p>
                        </div>
                    `;
                }}
            }}
            
            // テンプレート選択
            function selectTemplate(element, templateName, templateContent, applicationId) {{
                // 他の選択を解除
                document.querySelectorAll('.template-recommendation').forEach(el => {{
                    el.classList.remove('selected');
                }});
                
                // 選択されたテンプレートをハイライト
                element.classList.add('selected');
            }}
            
            // テンプレートを使用してメール生成
            async function generateEmailWithTemplate(applicationId, templateName, templateContent) {{
                const modal = document.getElementById('aiModal');
                const modalBody = document.getElementById('aiModalBody');
                
                // ローディング表示
                modalBody.innerHTML = `
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <p>テンプレート「${{templateName}}」を参考にQwen3で文面を生成中...</p>
                    </div>
                `;
                
                try {{
                    const response = await fetch(`/api/generate-email-with-template/${{applicationId}}`, {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            template_name: templateName,
                            reference_template: templateContent
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        modalBody.innerHTML = `
                            <div class="ai-result">
                                <h4>✅ AI文面生成完了 (テンプレート: ${{result.template_name}})</h4>
                                <p><strong>件名:</strong></p>
                                <div class="ai-content">${{result.generated_subject}}</div>
                                <p><strong>本文:</strong></p>
                                <div class="ai-content">${{result.generated_body}}</div>
                                <button class="copy-button" onclick="copyToClipboard('${{result.generated_subject}}\\n\\n${{result.generated_body}}')">
                                    📋 クリップボードにコピー
                                </button>
                                <div style="margin-top: 15px; padding: 10px; background: #e8f5e8; border-radius: 4px; font-size: 0.9em;">
                                    <strong>生成情報:</strong> ${{result.context_used}}
                                </div>
                            </div>
                        `;
                    }} else {{
                        modalBody.innerHTML = `
                            <div class="ai-result">
                                <h4>❌ 生成に失敗しました</h4>
                                <p>エラー: ${{result.error}}</p>
                                <p><strong>フォールバック件名:</strong></p>
                                <div class="ai-content">${{result.generated_subject}}</div>
                                <p><strong>フォールバック本文:</strong></p>
                                <div class="ai-content">${{result.generated_body}}</div>
                            </div>
                        `;
                    }}
                }} catch (error) {{
                    modalBody.innerHTML = `
                        <div class="ai-result">
                            <h4>❌ エラーが発生しました</h4>
                            <p>テンプレート文面生成に失敗しました: ${{error.message}}</p>
                        </div>
                    `;
                }}
            }}
            
            // AI文面生成（自動テンプレート選択付き）
            async function generateAIEmail(applicationId) {{
                const modal = document.getElementById('aiModal');
                const modalBody = document.getElementById('aiModalBody');
                
                // モーダルを表示
                modal.style.display = 'block';
                
                // ローディング表示
                modalBody.innerHTML = `
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <p>🔍 最適なテンプレートを自動選択中...</p>
                    </div>
                `;
                
                try {{
                    // 1. まずテンプレート推奨を取得
                    const templateResponse = await fetch(`/api/template-recommendations/${{applicationId}}`);
                    const templateResult = await templateResponse.json();
                    
                    if (templateResult.success && templateResult.recommendations.length > 0) {{
                        // 最高スコアのテンプレートを自動選択
                        const bestTemplate = templateResult.recommendations[0];
                        
                        // ローディング表示を更新
                        modalBody.innerHTML = `
                            <div class="loading-spinner">
                                <div class="spinner"></div>
                                <p>🤖 テンプレート「${{bestTemplate.template_name}}」を参考にQwen3で文面を生成中...</p>
                            </div>
                        `;
                        
                        // 2. 選択されたテンプレートでAI文面生成
                        const emailResponse = await fetch(`/api/generate-email-with-template/${{applicationId}}`, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: JSON.stringify({{
                                template_name: bestTemplate.template_name,
                                reference_template: bestTemplate.template_content
                            }})
                        }});
                        
                        const emailResult = await emailResponse.json();
                        
                        if (emailResult.success) {{
                            modalBody.innerHTML = `
                                <div class="ai-result">
                                    <h4>✅ AI文面生成完了</h4>
                                    <p style="color: #28a745; font-weight: bold;">
                                        📝 自動選択テンプレート: 「${{bestTemplate.template_name}}」
                                        <span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8em; margin-left: 8px;">
                                            適合度: ${{Math.round(bestTemplate.relevance_score * 100)}}%
                                        </span>
                                    </p>
                                </div>
                                
                                <div class="ai-result">
                                    <h4>📧 生成された件名</h4>
                                    <div class="ai-content">${{emailResult.generated_subject}}</div>
                                    <button class="copy-button" onclick="copyToClipboard('${{emailResult.generated_subject.replace(/'/g, "\\\\'")}}')">
                                        📋 件名をコピー
                                    </button>
                                </div>
                                
                                <div class="ai-result">
                                    <h4>📝 生成された本文</h4>
                                    <div class="ai-content">${{emailResult.generated_body}}</div>
                                                                    <button class="copy-button" onclick="copyToClipboard(`${{emailResult.generated_body.replace(/`/g, '\\\\`')}}`)">
                                    📋 本文をコピー
                                </button>
                                </div>
                                
                                <div class="ai-result" style="background: #e8f5e8; border: 1px solid #a5d6a7;">
                                    <h4>🔧 生成情報</h4>
                                    <p><strong>モデル:</strong> ${{emailResult.metadata.model || 'Qwen3:30b'}}</p>
                                    <p><strong>テンプレート:</strong> ${{emailResult.template_name}}</p>
                                    <p><strong>生成方式:</strong> テンプレート参考型</p>
                                    <p><strong>生成時刻:</strong> ${{new Date().toLocaleString('ja-JP')}}</p>
                                </div>
                                
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                                    <h4>📋 参考テンプレート</h4>
                                    <div style="background: #f0f0f0; padding: 15px; border-radius: 8px; font-size: 0.9em; color: #666; max-height: 200px; overflow-y: auto;">
                                        ${{bestTemplate.template_content}}
                                    </div>
                                    <p style="margin-top: 10px; font-size: 0.85em; color: #666;">
                                        <strong>選択理由:</strong> ${{bestTemplate.reason}}
                                    </p>
                                </div>
                                
                                <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">
                                    <p style="margin: 0; font-size: 0.9em; color: #856404;">
                                        💡 他のテンプレートを試したい場合は「📝 テンプレート提案」ボタンから選択できます。
                                    </p>
                                </div>
                            `;
                        }} else {{
                            modalBody.innerHTML = `
                                <div class="ai-result">
                                    <h4>❌ 生成に失敗しました</h4>
                                    <p>エラー: ${{emailResult.error}}</p>
                                    <p>選択テンプレート: ${{bestTemplate.template_name}}</p>
                                    <button class="send-button" onclick="showTemplateRecommendations('${{applicationId}}')">テンプレート提案を試す</button>
                                </div>
                            `;
                        }}
                        
                    }} else {{
                        // テンプレートが見つからない場合は通常生成にフォールバック
                        modalBody.innerHTML = `
                            <div class="loading-spinner">
                                <div class="spinner"></div>
                                <p>🤖 通常モードでQwen3文面生成中...</p>
                            </div>
                        `;
                        
                        const response = await fetch(`/api/generate-email/${{applicationId}}`, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }}
                        }});
                        
                        const result = await response.json();
                        
                        if (result.success) {{
                            modalBody.innerHTML = `
                                <div class="ai-result">
                                    <h4>📧 生成された件名</h4>
                                    <div class="ai-content">${{result.generated_subject}}</div>
                                    <button class="copy-button" onclick="copyToClipboard('${{result.generated_subject.replace(/'/g, "\\\\'")}}')">
                                        📋 件名をコピー
                                    </button>
                                </div>
                                
                                <div class="ai-result">
                                    <h4>📝 生成された本文</h4>
                                    <div class="ai-content">${{result.generated_body}}</div>
                                                                    <button class="copy-button" onclick="copyToClipboard(`${{result.generated_body.replace(/`/g, '\\\\`')}}`)">
                                    📋 本文をコピー
                                </button>
                                </div>
                                
                                <div class="ai-result" style="background: #fff3cd; border: 1px solid #ffeaa7;">
                                    <h4>⚠️ 通常生成モード</h4>
                                    <p><strong>モデル:</strong> ${{result.metadata.model || 'Qwen3:30b'}}</p>
                                    <p><strong>生成方式:</strong> テンプレート参考なし</p>
                                    <p><strong>生成時刻:</strong> ${{new Date().toLocaleString('ja-JP')}}</p>
                                    <p style="font-size: 0.9em; color: #856404;">適切なテンプレートが見つからなかったため、通常生成を使用しました。</p>
                                </div>
                            `;
                        }} else {{
                            modalBody.innerHTML = `
                                <div style="text-align: center; padding: 40px; color: #f44336;">
                                    <h4>❌ 生成に失敗しました</h4>
                                    <p>エラー: ${{result.error}}</p>
                                    <button class="send-button" onclick="closeAIModal()">閉じる</button>
                                </div>
                            `;
                        }}
                    }}
                    
                }} catch (error) {{
                    modalBody.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: #f44336;">
                            <h4>❌ 通信エラー</h4>
                            <p>サーバーとの通信に失敗しました: ${{error.message}}</p>
                            <button class="send-button" onclick="closeAIModal()">閉じる</button>
                        </div>
                    `;
                }}
            }}
            
            // モーダルを閉じる
            function closeAIModal() {{
                document.getElementById('aiModal').style.display = 'none';
            }}
            
            // クリップボードにコピー
            async function copyToClipboard(text) {{
                try {{
                    await navigator.clipboard.writeText(text);
                    alert('📋 クリップボードにコピーしました！');
                }} catch (err) {{
                    // フォールバック
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    alert('📋 クリップボードにコピーしました！');
                }}
            }}
            
            // モーダル外クリックで閉じる
            window.onclick = function(event) {{
                const modal = document.getElementById('aiModal');
                if (event.target == modal) {{
                    closeAIModal();
                }}
            }}
            
            // メッセージ展開/折り畳み機能
            function expandMessage(msgId) {{
                const truncatedContent = document.getElementById(msgId + '_content');
                const fullContent = document.getElementById(msgId + '_full');
                const expandButton = document.getElementById(msgId + '_expand');
                const collapseButton = document.getElementById(msgId + '_collapse');
                
                // アニメーション効果
                truncatedContent.style.display = 'none';
                fullContent.style.display = 'block';
                fullContent.classList.add('expanding');
                
                // ボタンの表示切り替え
                expandButton.style.display = 'none';
                collapseButton.style.display = 'inline-block';
                
                // スクロール位置を調整（オプション）
                setTimeout(() => {{
                    fullContent.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                }}, 100);
            }}
            
            function collapseMessage(msgId) {{
                const truncatedContent = document.getElementById(msgId + '_content');
                const fullContent = document.getElementById(msgId + '_full');
                const expandButton = document.getElementById(msgId + '_expand');
                const collapseButton = document.getElementById(msgId + '_collapse');
                
                // アニメーション効果
                fullContent.classList.remove('expanding');
                fullContent.classList.add('collapsing');
                
                setTimeout(() => {{
                    fullContent.style.display = 'none';
                    truncatedContent.style.display = 'block';
                    fullContent.classList.remove('collapsing');
                    
                    // ボタンの表示切り替え
                    expandButton.style.display = 'inline-block';
                    collapseButton.style.display = 'none';
                }}, 300);
            }}
            
            // 全てのメッセージを一括展開/折り畳み
            function expandAllMessages() {{
                const expandButtons = document.querySelectorAll('.expand-button');
                expandButtons.forEach(button => {{
                    if (button.style.display !== 'none') {{
                        const msgId = button.id.replace('_expand', '');
                        expandMessage(msgId);
                    }}
                }});
            }}
            
            function collapseAllMessages() {{
                const collapseButtons = document.querySelectorAll('.collapse-button');
                collapseButtons.forEach(button => {{
                    if (button.style.display !== 'none') {{
                        const msgId = button.id.replace('_collapse', '');
                        collapseMessage(msgId);
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_content

def generate_timeline_html(messages):
    """タイムライン HTML生成（展開/折り畳み機能付き）"""
    if not messages:
        return "<p>履歴がありません。</p>"
    
    html = ""
    for index, msg in enumerate(messages):
        msg_id = f"msg_{index}"
        type_class = f"type-{msg.message_type.replace('_', '-')}"
        direction = "送信" if msg.is_outbound else "受信"
        icon = {"email_sent": "📧", "email_received": "📨", "interview": "💬", "note": "📝", "internal_note": "🔄"}.get(msg.message_type, "📄")
        
        # 4行以上の場合は省略表示機能を付与
        content_lines = msg.content.split('\n')
        content_length = len(msg.content)
        should_truncate = len(content_lines) > 4
        
        if should_truncate:
            truncated_lines = content_lines[:4]
            truncated_content = '\n'.join(truncated_lines) + "\n..."
            full_content = msg.content
            
            html += f"""
            <div class="timeline-item">
                <div class="timeline-header">
                    <span class="timeline-time">{msg.timestamp}</span>
                    <span class="timeline-type {type_class}">{icon} {msg.message_type.replace('_', ' ').title()}</span>
                    <span class="message-length">({content_length}文字)</span>
                </div>
                <div style="font-weight: bold; margin-bottom: 5px;">
                    {msg.subject}
                </div>
                <div style="font-size: 0.9em; color: #666; margin-bottom: 8px;">
                    {msg.sender} → {msg.receiver}
                </div>
                <div class="timeline-content" id="{msg_id}_content">
                    {truncated_content.replace(chr(10), '<br>')}
                </div>
                <div class="timeline-content" id="{msg_id}_full" style="display: none;">
                    {full_content.replace(chr(10), '<br>')}
                </div>
                <div class="expand-controls">
                    <button class="expand-button" id="{msg_id}_expand" onclick="expandMessage('{msg_id}')">
                        📖 全文を表示
                    </button>
                    <button class="collapse-button" id="{msg_id}_collapse" onclick="collapseMessage('{msg_id}')" style="display: none;">
                        📝 要約表示
                    </button>
                </div>
            </div>
            """
        else:
            html += f"""
            <div class="timeline-item">
                <div class="timeline-header">
                    <span class="timeline-time">{msg.timestamp}</span>
                    <span class="timeline-type {type_class}">{icon} {msg.message_type.replace('_', ' ').title()}</span>
                    <span class="message-length">({content_length}文字)</span>
                </div>
                <div style="font-weight: bold; margin-bottom: 5px;">
                    {msg.subject}
                </div>
                <div style="font-size: 0.9em; color: #666; margin-bottom: 8px;">
                    {msg.sender} → {msg.receiver}
                </div>
                <div class="timeline-content">
                    {msg.content.replace(chr(10), '<br>')}
                </div>
            </div>
            """
    return html

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """ダッシュボード - ブラウザで確認可能な画面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CA Support System - ダッシュボード</title>
        <style>
            body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
            .header h1 { margin: 0; font-size: 2.5em; }
            .header p { margin: 10px 0 0 0; opacity: 0.9; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
            .stat-number { font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 5px; }
            .stat-label { color: #666; font-size: 0.9em; }
            .section { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .section h2 { margin-top: 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
            .application-list, .task-list { display: grid; gap: 15px; }
            .application-item, .task-item { padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #fafafa; cursor: pointer; transition: all 0.3s; }
            .application-item:hover, .task-item:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); transform: translateY(-2px); }
            .application-header, .task-header { font-weight: bold; color: #333; margin-bottom: 8px; }
            .status { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; color: white; }
            .status.reviewing { background-color: #ff9800; }
            .status.interviewing { background-color: #2196f3; }
            .status.offered { background-color: #4caf50; }
            .priority { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
            .priority.high { background-color: #f44336; color: white; }
            .priority.medium { background-color: #ff9800; color: white; }
            .priority.low { background-color: #4caf50; color: white; }
            .score { display: inline-block; margin: 5px; }
            .score-label { font-size: 0.8em; color: #666; }
            .score-value { font-weight: bold; color: #667eea; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 CA Support System</h1>
                <p>キャリアアドバイザー支援システム - デモ版</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">3</div>
                    <div class="stat-label">進行中の案件</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">4</div>
                    <div class="stat-label">未完了タスク</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">3</div>
                    <div class="stat-label">候補者</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">2</div>
                    <div class="stat-label">緊急タスク</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📋 進行中の案件</h2>
                <div class="application-list" id="applications">
                    <!-- Applications will be loaded here -->
                </div>
            </div>
            
            <div class="section">
                <h2>📝 未完了タスク</h2>
                <div class="task-list" id="tasks">
                    <!-- Tasks will be loaded here -->
                </div>
            </div>
        </div>
        
        <script>
            // アプリケーションデータの読み込み
            fetch('/api/applications')
                .then(response => response.json())
                .then(applications => {
                    const container = document.getElementById('applications');
                    container.innerHTML = applications.map(app => `
                        <div class="application-item" onclick="window.location.href='/application/${app.id}'">
                            <div class="application-header">
                                ${app.candidate_name} → ${app.company} (${app.job_title})
                            </div>
                            <div>
                                <span class="status ${app.status.includes('書類') ? 'reviewing' : app.status.includes('面接') ? 'interviewing' : 'offered'}">
                                    ${app.status}
                                </span>
                                <span class="score">
                                    <span class="score-label">熱意:</span>
                                    <span class="score-value">${(app.enthusiasm_score * 100).toFixed(0)}%</span>
                                </span>
                                <span class="score">
                                    <span class="score-label">懸念:</span>
                                    <span class="score-value">${(app.concern_score * 100).toFixed(0)}%</span>
                                </span>
                            </div>
                            <div style="margin-top: 8px; color: #666; font-size: 0.9em;">
                                ${app.latest_summary}
                            </div>
                        </div>
                    `).join('');
                });
            
            // タスクデータの読み込み
            fetch('/api/tasks')
                .then(response => response.json())
                .then(tasks => {
                    const container = document.getElementById('tasks');
                    container.innerHTML = tasks.map(task => `
                        <div class="task-item">
                            <div class="task-header">
                                ${task.description}
                            </div>
                            <div>
                                <span class="priority ${task.priority}">${task.priority.toUpperCase()}</span>
                                <span style="margin-left: 10px; color: #666;">
                                    担当: ${task.owner} | 期限: ${task.due}
                                </span>
                            </div>
                            <div style="margin-top: 5px; color: #666; font-size: 0.9em;">
                                ${task.candidate_name} - ${task.company}
                            </div>
                        </div>
                    `).join('');
                });
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    print("🚀 CA Support System デモ版を起動しています...")
    print("📊 ダッシュボード: http://localhost:8000/dashboard")
    print("📚 API ドキュメント: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000) 