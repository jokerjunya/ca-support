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

# FastAPIアプリケーション
app = FastAPI(
    title="CA Support System - デモ版",
    description="キャリアアドバイザー支援システムのデモ版",
    version="0.1.0"
)

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

# メッセージ履歴
sample_message_history = [
    # 田中太郎の履歴
    MessageHistory(
        id="msg_001",
        application_id="app_001",
        timestamp="2024-01-08 09:00",
        message_type="note",
        sender="System",
        receiver="CA",
        subject="応募受理",
        content="田中太郎様からAcme株式会社シニアエンジニア職への応募を受理しました。",
        is_outbound=False
    ),
    MessageHistory(
        id="msg_002",
        application_id="app_001",
        timestamp="2024-01-10 14:30",
        message_type="email_sent",
        sender="CA",
        receiver="田中太郎",
        subject="書類選考結果について",
        content="田中様、書類選考の結果についてお知らせします。技術力については問題ありませんが、転職理由について詳しくお聞かせください。面談の機会を設けさせていただければと思います。",
        is_outbound=True
    ),
    MessageHistory(
        id="msg_003",
        application_id="app_001",
        timestamp="2024-01-12 16:45",
        message_type="email_received",
        sender="田中太郎",
        receiver="CA",
        subject="Re: 書類選考結果について",
        content="ご連絡ありがとうございます。転職理由について詳しくお話しさせていただきたいです。来週でしたらいつでも面談可能です。",
        is_outbound=False
    ),
    MessageHistory(
        id="msg_004",
        application_id="app_001",
        timestamp="2024-01-15 10:00",
        message_type="interview",
        sender="CA",
        receiver="田中太郎",
        subject="面談実施",
        content="【面談記録】転職理由：現在の職場でのキャリアアップが難しく、より技術的に挑戦できる環境を求めている。年収面での不満もあり。技術スキルは高く、特にPythonとAWSに精通。人柄も良好で、面接通過の可能性高い。",
        is_outbound=False
    )
]

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
    messages = [m for m in sample_message_history if m.application_id == application_id]
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

@app.get("/application/{application_id}", response_class=HTMLResponse)
async def application_detail_page(application_id: str):
    """案件詳細画面"""
    # データ取得
    app = next((a for a in sample_applications if a.id == application_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    next_action = next((a for a in sample_next_actions if a.application_id == application_id), None)
    messages = [m for m in sample_message_history if m.application_id == application_id]
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
            .timeline {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .timeline h2 {{ margin-top: 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            .timeline-item {{ padding: 15px 0; border-bottom: 1px solid #eee; }}
            .timeline-item:last-child {{ border-bottom: none; }}
            .timeline-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 8px; }}
            .timeline-time {{ color: #666; font-size: 0.9em; }}
            .timeline-type {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-left: 10px; }}
            .type-email-sent {{ background: #e3f2fd; color: #1976d2; }}
            .type-email-received {{ background: #f3e5f5; color: #7b1fa2; }}
            .type-interview {{ background: #e8f5e8; color: #388e3c; }}
            .type-note {{ background: #fff3e0; color: #f57c00; }}
            .timeline-content {{ color: #333; line-height: 1.5; }}
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
                        <button class="send-button" style="background: #6c757d; margin-left: 10px;" onclick="alert('AI文面生成は開発中です')">
                            🤖 AI文面生成
                        </button>
                    </div>
                </div>
            </div>
            ''' if next_action else ''}
            
            <div class="timeline">
                <h2>📜 履歴タイムライン</h2>
                {generate_timeline_html(messages)}
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_timeline_html(messages):
    """タイムライン HTML生成"""
    if not messages:
        return "<p>履歴がありません。</p>"
    
    html = ""
    for msg in messages:
        type_class = f"type-{msg.message_type.replace('_', '-')}"
        direction = "送信" if msg.is_outbound else "受信"
        icon = {"email_sent": "📧", "email_received": "📨", "interview": "💬", "note": "📝"}.get(msg.message_type, "📄")
        
        html += f"""
        <div class="timeline-item">
            <div class="timeline-header">
                <span class="timeline-time">{msg.timestamp}</span>
                <span class="timeline-type {type_class}">{icon} {msg.message_type.replace('_', ' ').title()}</span>
            </div>
            <div style="font-weight: bold; margin-bottom: 5px;">
                {msg.subject}
            </div>
            <div style="font-size: 0.9em; color: #666; margin-bottom: 8px;">
                {msg.sender} → {msg.receiver}
            </div>
            <div class="timeline-content">
                {msg.content}
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