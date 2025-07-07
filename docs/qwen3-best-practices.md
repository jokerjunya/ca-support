# Qwen3 ベストプラクティス & 開発ガイド

このドキュメントでは、Qwen3を使用したアプリケーション開発における最適な手法とベストプラクティスをまとめています。

## 📋 目次

- [Qwen3概要](#qwen3概要)
- [プロンプトエンジニアリング](#プロンプトエンジニアリング)
- [モデル選択と設定](#モデル選択と設定)
- [アプリケーション開発](#アプリケーション開発)
- [パフォーマンス最適化](#パフォーマンス最適化)
- [セキュリティ考慮事項](#セキュリティ考慮事項)
- [実装パターン](#実装パターン)
- [トラブルシューティング](#トラブルシューティング)

## 🤖 Qwen3概要

### モデルラインナップ

**Dense Models (密集型)**
- Qwen3-0.6B: 軽量デバイス向け
- Qwen3-1.7B: モバイル・エッジ向け
- Qwen3-4B: ローカル実行に最適
- Qwen3-8B: バランスの良い性能
- Qwen3-14B: 高性能アプリケーション
- Qwen3-32B: 最高性能Dense

**MoE Models (Mixture of Experts)**
- Qwen3-30B-A3B: 3B活性化、効率重視
- Qwen3-235B-A22B: 22B活性化、最高性能

### 特徴
- **Apache 2.0ライセンス**: 商用利用可能
- **119言語サポート**: 多言語アプリケーション対応
- **ハイブリッド思考**: Thinking/Non-Thinkingモード切替
- **長文対応**: 最大128Kトークンコンテキスト

## 🎯 プロンプトエンジニアリング

### 1. 基本原則

#### 言語の選択
```markdown
❌ 避けるべき：
日本語でプロンプトを書く

✅ 推奨：
英語でプロンプトを書き、日本語出力を指定
```

**理由**: Qwen3は英語でのトレーニングが最も充実しており、英語プロンプトで最高品質の出力を得られます。

#### プロンプト構造
```text
あなたは{役割}です。以下の情報を基に、{対象者}宛の{目的}を作成してください。

## 背景情報
{詳細な背景}

## 要求事項
1. {具体的要求1}
2. {具体的要求2}
3. {具体的要求3}

## 出力形式
{期待する形式}

以下の形式で日本語で回答してください：
{テンプレート}
```

### 2. モード切替

#### Thinking Mode（推論モード）
```python
# 複雑な問題や論理的推論が必要な場合
messages = [{"role": "user", "content": "複雑な分析タスク"}]
response = client.chat.completions.create(
    model="qwen3-30b-a3b",
    messages=messages,
    extra_body={"enable_thinking": True},  # Thinking Mode有効化
    temperature=0.6,  # 創造性とバランス
    max_tokens=1000
)
```

#### Non-Thinking Mode（高速モード）
```python
# 単純なタスクや高速応答が必要な場合
response = client.chat.completions.create(
    model="qwen3-30b-a3b",
    messages=messages,
    extra_body={"reasoning_effort": "none"},  # Non-Thinking Mode
    temperature=0.7,  # 少し高めの創造性
    max_tokens=500
)
```

### 3. プロンプトテンプレート

#### メール文面生成（推奨例）
```text
You are an experienced career advisor with 10+ years of expertise. 
Create an effective email for {target_person} based on the detailed information below.

## Case Details
- Candidate: {candidate_name}
- Company: {company}
- Position: {job_title}
- Current Status: {status}
- Enthusiasm Level: {enthusiasm_score}% (higher = more positive)
- Concern Level: {concern_score}% (higher = more worried)

## Situation Details and History
{detailed_context_with_history}

## Requirements
Create a practical and human email that includes:

1. **Appropriate Length**: 200-500 characters
2. **Specific Content**: Concrete proposals based on past interactions
3. **Next Steps**: Clear and actionable actions
4. **Appropriate Tone**: Polite but not too formal, friendly
5. **Personal Consideration**: Reflect candidate's concerns and hopes

## Target Audience Considerations
- CS (Corporate Representative): Balance candidate's appeal and concerns
- Candidate: Content that alleviates anxiety and maintains positive feelings
- RA (Recruiting Advisor): Clearly communicate current status and needed support

Please respond in Japanese in the following format:
Subject: [subject]
Body: [body]
```

## 🎛️ モデル選択と設定

### 用途別推奨モデル

| 用途 | 推奨モデル | 理由 |
|------|------------|------|
| チャットボット | Qwen3-4B | 高速、低コスト |
| コード生成 | Qwen3-14B | バランス良い性能 |
| 文書分析 | Qwen3-30B-A3B | 長文対応、効率的 |
| 複雑な推論 | Qwen3-235B-A22B | 最高性能 |
| モバイルアプリ | Qwen3-0.6B/1.7B | 軽量 |

### パラメータ設定

#### Thinking Mode
```python
thinking_params = {
    "temperature": 0.6,      # バランスの良い創造性
    "top_p": 0.95,          # 多様性確保
    "top_k": 20,            # 品質重視
    "max_tokens": 1000,     # 詳細な推論用
    "enable_thinking": True
}
```

#### Non-Thinking Mode
```python
fast_params = {
    "temperature": 0.7,     # 少し高めの創造性
    "top_p": 0.8,          # 効率重視
    "max_tokens": 500,     # 高速応答
    "reasoning_effort": "none"
}
```

## 🏗️ アプリケーション開発

### 1. 基本的な統合パターン

#### シンプルな統合
```python
from app.core.llm import QwenLLM

class EmailGenerator:
    def __init__(self):
        self.llm = QwenLLM(
            base_url="http://localhost:11434",
            model_name="qwen3:30b"
        )
    
    def generate_email(self, context):
        try:
            result = self.llm.generate_email_content(context)
            return {
                "success": True,
                "content": result["body"],
                "subject": result["subject"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": self._generate_fallback(context)
            }
```

### 2. エラーハンドリング

#### 堅牢なエラー処理
```python
async def robust_generation(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            # メイン生成処理
            response = await generate_with_qwen3(query)
            
            # 品質チェック
            if quality_check(response):
                return response
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt == max_retries - 1:
                # 最終的にフォールバック
                return generate_fallback_response(query)
            
            # 指数バックオフで再試行
            await asyncio.sleep(2 ** attempt)
```

### 3. コンテキスト管理

#### 履歴情報の統合
```python
def build_context_with_history(application_id):
    """履歴情報を含む詳細コンテキストを構築"""
    # 基本情報取得
    app = get_application(application_id)
    
    # 関連メッセージ履歴取得
    messages = get_message_history(application_id)
    messages.sort(key=lambda x: x.timestamp)
    
    # 履歴をコンテキストに統合
    history_context = ""
    if messages:
        history_context = "\n\n## Past Communication History\n"
        for msg in messages[-3:]:  # 最新3件
            direction = "sent" if msg.is_outbound else "received"
            history_context += f"""
### {msg.timestamp} - {direction}
**{msg.sender} → {msg.receiver}**
Subject: {msg.subject}
Content: {msg.content}
"""
    
    return EmailGenerationContext(
        candidate_name=app.candidate_name,
        company=app.company,
        job_title=app.job_title,
        status=app.status,
        latest_summary=app.latest_summary + history_context,
        enthusiasm_score=app.enthusiasm_score,
        concern_score=app.concern_score,
        target_person=get_target_person(application_id),
        current_template=get_template(application_id)
    )
```

## ⚡ パフォーマンス最適化

### 1. 段階的品質向上

```python
async def adaptive_generation(query, quality_threshold=0.8):
    """段階的に品質を向上させる生成手法"""
    
    # 1. 高速生成（Non-thinking）
    quick_response = await generate_fast(query)
    
    # 2. 品質評価
    quality_score = evaluate_quality(quick_response)
    
    if quality_score >= quality_threshold:
        return quick_response
    
    # 3. 高品質生成（Thinking）
    logger.info("Quality below threshold, using thinking mode")
    return await generate_with_thinking(query)
```

### 2. コスト効率パターン

```python
def cost_efficient_workflow(query, complexity_threshold=0.7):
    """コスト効率を考慮したモデル選択"""
    
    # 複雑度判定
    complexity = analyze_complexity(query)
    
    if complexity < complexity_threshold:
        # 簡単なタスクは小さいモデルで
        return qwen3_4b.generate(query)
    else:
        # 複雑なタスクは大きいモデルで
        return qwen3_30b.generate(query)
```

### 3. キャッシュ戦略

```python
import hashlib
from functools import lru_cache

class ResponseCache:
    def __init__(self):
        self.cache = {}
    
    def get_cache_key(self, context):
        """コンテキストからキャッシュキーを生成"""
        content = f"{context.candidate_name}_{context.company}_{context.status}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_response(self, context):
        key = self.get_cache_key(context)
        return self.cache.get(key)
    
    def cache_response(self, context, response):
        key = self.get_cache_key(context)
        self.cache[key] = response
```

## 🔒 セキュリティ考慮事項

### 1. プロンプトインジェクション対策

```python
import re

def sanitize_user_input(user_input):
    """ユーザー入力のサニタイズ"""
    
    # 危険なパターンを除去
    dangerous_patterns = [
        r"ignore\s+previous\s+instructions",
        r"forget\s+your\s+role",
        r"act\s+as\s+if",
        r"pretend\s+to\s+be",
        r"<think>.*?</think>",  # 思考プロセスの偽装防止
    ]
    
    cleaned_input = user_input
    for pattern in dangerous_patterns:
        cleaned_input = re.sub(pattern, "", cleaned_input, flags=re.IGNORECASE)
    
    return cleaned_input.strip()
```

### 2. 機密情報保護

```python
def contains_sensitive_data(text):
    """機密情報の検出"""
    sensitive_patterns = [
        r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",  # クレジットカード
        r"\b\d{3}-\d{2}-\d{4}\b",        # SSN
        r"password\s*[=:]\s*\w+",        # パスワード
        r"api[_-]?key\s*[=:]\s*\w+",     # APIキー
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
```

### 3. レート制限

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=60, window_minutes=1):
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id):
        now = datetime.now()
        
        # 古いリクエストを削除
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window
        ]
        
        # レート制限チェック
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # リクエストを記録
        self.requests[user_id].append(now)
        return True
```

## 🔧 実装パターン

### 1. ファクトリーパターン

```python
class QwenModelFactory:
    @staticmethod
    def create_model(model_type, use_case):
        """用途に応じた最適なモデルを生成"""
        
        configs = {
            "chat": {
                "small": QwenConfig("qwen3:4b", temperature=0.7),
                "medium": QwenConfig("qwen3:14b", temperature=0.6),
                "large": QwenConfig("qwen3:30b-a3b", temperature=0.5)
            },
            "analysis": {
                "fast": QwenConfig("qwen3:8b", reasoning_effort="none"),
                "accurate": QwenConfig("qwen3:30b-a3b", enable_thinking=True)
            }
        }
        
        config = configs.get(model_type, {}).get(use_case)
        if not config:
            raise ValueError(f"Unknown model type: {model_type}/{use_case}")
        
        return QwenLLM(config)
```

### 2. デコレーターパターン

```python
def with_retry_and_fallback(max_retries=3):
    """再試行とフォールバック機能を追加するデコレーター"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
            
            # フォールバック処理
            logger.error(f"All attempts failed: {last_error}")
            return generate_fallback_response(*args, **kwargs)
        
        return wrapper
    return decorator

@with_retry_and_fallback(max_retries=2)
async def generate_email_content(context):
    return await qwen3_llm.generate(context)
```

### 3. オブザーバーパターン

```python
class GenerationEventObserver:
    def __init__(self):
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_generation_start(self, context):
        for observer in self.observers:
            observer.on_generation_start(context)
    
    def notify_generation_complete(self, context, result):
        for observer in self.observers:
            observer.on_generation_complete(context, result)

class MetricsObserver:
    def on_generation_start(self, context):
        self.start_time = time.time()
    
    def on_generation_complete(self, context, result):
        duration = time.time() - self.start_time
        log_metrics(context, result, duration)
```

## 🛠️ トラブルシューティング

### よくある問題と解決策

#### 1. 生成品質が低い
```python
# 問題: 期待する品質の出力が得られない
# 解決策:

# A. プロンプトを英語で書き直す
prompt = """
You are an experienced career advisor. Create a professional email...
(Respond in Japanese)
"""

# B. Thinking Modeを有効化
response = llm.generate(prompt, enable_thinking=True)

# C. temperatureを調整
response = llm.generate(prompt, temperature=0.6)  # より一貫性重視
```

#### 2. レスポンスが遅い
```python
# 問題: 生成に時間がかかりすぎる
# 解決策:

# A. Non-thinking Modeを使用
response = llm.generate(prompt, reasoning_effort="none")

# B. 小さいモデルを使用
llm = QwenLLM(model_name="qwen3:4b")

# C. max_tokensを制限
response = llm.generate(prompt, max_tokens=300)
```

#### 3. メモリ不足
```python
# 問題: モデルがメモリに収まらない
# 解決策:

# A. 量子化モデルを使用
model_name = "qwen3:30b-a3b-q4_0"  # 4bit量子化

# B. より小さいモデルに変更
model_name = "qwen3:8b"

# C. MoEモデルを活用
model_name = "qwen3:30b-a3b"  # 3B活性化のみ
```

#### 4. API接続エラー
```python
# 問題: Ollama APIに接続できない
# 解決策:

# A. 接続確認
def check_ollama_connection():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False

# B. リトライ機能
async def robust_api_call(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await llm.generate(prompt)
        except ConnectionError:
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
            else:
                raise
```

## 📈 モニタリング

### メトリクス収集

```python
class QwenMetrics:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0,
            "thinking_mode_usage": 0,
            "error_count": 0
        }
    
    def record_request(self, success, response_time, used_thinking_mode):
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["error_count"] += 1
        
        if used_thinking_mode:
            self.metrics["thinking_mode_usage"] += 1
        
        # 平均応答時間の更新
        self._update_average_response_time(response_time)
    
    def get_success_rate(self):
        if self.metrics["total_requests"] == 0:
            return 0
        return self.metrics["successful_requests"] / self.metrics["total_requests"]
```

## 🎉 まとめ

Qwen3を効果的に活用するための重要なポイント：

1. **英語プロンプト + 日本語出力指定** で最高品質を実現
2. **用途に応じたモード選択** でパフォーマンスを最適化
3. **適切なモデルサイズ選択** でコストとリソースのバランス
4. **堅牢なエラーハンドリング** で安定したサービス提供
5. **セキュリティ対策** でリスクを最小化
6. **継続的なモニタリング** で品質向上

これらのベストプラクティスを実装することで、Qwen3の能力を最大限に活用した高品質なAIアプリケーションを構築できます。

---

**更新日**: 2025年1月21日  
**バージョン**: v1.0  
**次回更新予定**: 新機能リリース時 