"""
LLM統合モジュール - Qwen3 (Ollama) 連携
"""
import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EmailGenerationContext:
    """メール生成用のコンテキスト"""
    candidate_name: str
    company: str
    job_title: str
    status: str
    latest_summary: str
    enthusiasm_score: float
    concern_score: float
    target_person: str  # "CS", "candidate", "RA"
    current_template: str
    reference_template: Optional[str] = None  # 参考テンプレート
    template_name: Optional[str] = None  # テンプレート名
    

class QwenLLM:
    """Qwen3 (Ollama) LLM統合クラス"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "qwen3:30b"):
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/api/generate"
    
    def _call_ollama(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Ollama APIを呼び出す"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except Exception as e:
            print(f"Ollama API エラー: {e}")
            return f"エラー: LLM通信に失敗しました ({str(e)})"
    
    def generate_email_content(self, context: EmailGenerationContext) -> Dict[str, str]:
        """メール文面を生成する"""
        
        # テンプレート参考の場合とそうでない場合でプロンプトを変える
        if context.reference_template:
            # テンプレートを参考にした文章生成
            prompt = f"""あなたは10年以上の経験を持つプロフェッショナルなキャリアアドバイザーです。
以下の参考テンプレートを基に、具体的な状況に合わせて{context.target_person}宛のメール文面を作成してください。

## 参考テンプレート「{context.template_name}」
{context.reference_template}

## 案件の詳細情報
- 候補者: {context.candidate_name}様
- 企業: {context.company}
- 職種: {context.job_title}
- 現在の状況: {context.status}
- 熱意レベル: {context.enthusiasm_score * 100:.0f}%（高いほど前向き）
- 懸念レベル: {context.concern_score * 100:.0f}%（高いほど心配事が多い）

## 状況の詳細と過去の経緯
{context.latest_summary}

## 作成指示
参考テンプレートの構造と文体を参考にしつつ、以下の要素を含む実用的なメール文面を作成してください：

1. **テンプレート活用**: 参考テンプレートの構造・文体・表現を活かす
2. **情報置換**: ●●や○○などのプレースホルダーを具体的な情報に置換
3. **状況反映**: 候補者の熱意や懸念の状況を考慮した適切なトーン調整
4. **個人化**: 候補者の名前、企業名、職種などを正確に反映
5. **カスタマイズ**: 過去の経緯や現在の状況に応じた内容の追加・修正

## 送信対象者に応じた考慮事項
- CS（企業担当者）: 候補者の魅力と懸念点をバランス良く伝える
- 候補者: 不安を解消し、前向きな気持ちを維持できる内容
- RA（リクルーティングアドバイザー）: 現状と必要な支援を明確に伝える

以下の形式で必ず回答してください：
件名: [件名]
本文: [本文]"""
        else:
            # 通常の文章生成
            prompt = f"""あなたは10年以上の経験を持つプロフェッショナルなキャリアアドバイザーです。
以下の詳細情報を基に、{context.target_person}宛の効果的なメール文面を作成してください。

## 案件の詳細情報
- 候補者: {context.candidate_name}様
- 企業: {context.company}
- 職種: {context.job_title}
- 現在の状況: {context.status}
- 熱意レベル: {context.enthusiasm_score * 100:.0f}%（高いほど前向き）
- 懸念レベル: {context.concern_score * 100:.0f}%（高いほど心配事が多い）

## 状況の詳細と過去の経緯
{context.latest_summary}

## 作成指示
以下の要素を含む、実用的で人間味のあるメール文面を作成してください：

1. **適切な文字数**: 200-500文字程度
2. **具体的な内容**: 過去のやり取りを踏まえた具体的な提案
3. **次のステップ**: 明確で実行可能なアクション
4. **適切なトーン**: 丁寧だが堅すぎない、親しみやすい文体
5. **個人的な配慮**: 候補者の懸念や希望を反映

## 送信対象者に応じた考慮事項
- CS（企業担当者）: 候補者の魅力と懸念点をバランス良く伝える
- 候補者: 不安を解消し、前向きな気持ちを維持できる内容
- RA（リクルーティングアドバイザー）: 現状と必要な支援を明確に伝える

以下の形式で必ず回答してください：
件名: [件名]
本文: [本文]"""

        # LLM呼び出し（より高品質な文章を生成するために設定を最適化）
        response = self._call_ollama(prompt, temperature=0.6, max_tokens=1000)
        
        # レスポンスをパース
        try:
            # デフォルト値を設定（実際の処理で使用されないように特殊な値を設定）
            subject = "__DEFAULT_SUBJECT__"
            body = "__DEFAULT_BODY__"
            
            # 思考プロセス除去
            clean_response = response
            if "<think>" in clean_response:
                if "</think>" in clean_response:
                    # <think>...</think>の部分を削除
                    start_idx = clean_response.find("<think>")
                    end_idx = clean_response.find("</think>") + len("</think>")
                    clean_response = clean_response[:start_idx] + clean_response[end_idx:]
                    clean_response = clean_response.strip()
                else:
                    # </think>がない場合の処理を改善
                    # Qwen3の出力パターンに基づき、件名:または本文:を探す
                    lines = clean_response.split('\n')
                    actual_response_lines = []
                    capture_response = False
                    
                    for line in lines:
                        line = line.strip()
                        # 件名:または本文:が見つかったら、そこから先をキャプチャ開始
                        if (line.startswith("件名:") or line.startswith("件名：") or 
                            line.startswith("本文:") or line.startswith("本文：")):
                            capture_response = True
                        
                        # キャプチャモードの場合、この行と以降の行を含める
                        if capture_response and line:
                            actual_response_lines.append(line)
                    
                    if actual_response_lines:
                        clean_response = '\n'.join(actual_response_lines)
                    else:
                        # フォールバック：<think>以前の部分をチェック
                        before_think = clean_response.split("<think>")[0].strip()
                        if before_think:
                            clean_response = before_think
                        else:
                            clean_response = clean_response.strip()
            
            # 件名と本文を抽出
            lines = clean_response.split('\n')
            current_section = None
            body_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 件名の抽出
                if line.startswith("件名:") or line.startswith("件名："):
                    subject_part = line.split(":", 1)[1] if ":" in line else line.split("：", 1)[1]
                    subject = subject_part.strip()
                    current_section = "subject"
                elif line.startswith("本文:") or line.startswith("本文："):
                    body_part = line.split(":", 1)[1] if ":" in line else line.split("：", 1)[1]
                    if body_part.strip():
                        body_lines.append(body_part.strip())
                    current_section = "body"
                elif current_section == "body":
                    body_lines.append(line)
                elif current_section is None and line and not line.startswith("件名") and not line.startswith("本文"):
                    # 形式が整っていない場合、全体を本文として扱う
                    body_lines.append(line)
            
            # 本文の組み立て
            if body_lines:
                body = '\n'.join(body_lines)
            elif current_section is None:
                # 形式が全く整っていない場合、全体を本文として使用
                body = clean_response
            
            # 件名が抽出されなかった場合のフォールバック
            if not subject or subject.strip() == "" or subject == "__DEFAULT_SUBJECT__":
                if context.reference_template and context.template_name:
                    subject = f"【{context.candidate_name}様】{context.company}の件について"
                else:
                    subject = f"【{context.candidate_name}様】{context.company}案件の件"
            
            # 本文が抽出されなかった場合のフォールバック
            if not body or body.strip() == "" or body == "__DEFAULT_BODY__":
                body = f"お疲れ様です。{context.candidate_name}様の{context.company}の件についてご連絡いたします。\n\n詳細は別途お話しさせていただければと思います。"
            
            # デバッグ情報を出力
            print(f"[DEBUG] 生レスポンス長: {len(response)}")
            print(f"[DEBUG] クリーンレスポンス長: {len(clean_response)}")
            print(f"[DEBUG] 抽出された件名: {subject}")
            print(f"[DEBUG] 抽出された本文長: {len(body)}")
            
            return {
                "subject": subject,
                "body": body,
                "metadata": {
                    "model": self.model_name,
                    "temperature": 0.6,
                    "context_length": len(prompt),
                    "has_reference_template": bool(context.reference_template),
                    "template_name": context.template_name or "なし"
                },
                "raw_response": response  # デバッグ用
            }
            
        except Exception as e:
            print(f"レスポンス解析エラー: {e}")
            print(f"生レスポンス: {response}")
            print(f"クリーンレスポンス: {clean_response}")
            return {
                "subject": f"【{context.candidate_name}様】{context.company}の件について",
                "body": f"お疲れ様です。{context.candidate_name}様の{context.company}の件についてご連絡いたします。\n\nエラーが発生したため、詳細は別途お話しさせていただければと思います。",
                "metadata": {
                    "model": self.model_name,
                    "error": str(e),
                    "has_reference_template": bool(context.reference_template),
                    "template_name": context.template_name or "なし"
                },
                "raw_response": response
            }

    def analyze_email_content(self, email_content: str) -> Dict[str, Any]:
        """メール内容を解析してスコアを算出"""
        
        prompt = f"""以下のメール内容を分析して、候補者の熱意と懸念を0-1の範囲で評価してください。

メール内容:
{email_content}

以下の形式で回答してください：
熱意スコア: [0-1の値]
懸念スコア: [0-1の値]
分析理由: [理由]"""

        response = self._call_ollama(prompt, temperature=0.3, max_tokens=300)
        
        try:
            # スコアを抽出
            enthusiasm_score = 0.5
            concern_score = 0.5
            analysis_reason = "分析できませんでした"
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("熱意スコア:"):
                    try:
                        enthusiasm_score = float(line.split(":", 1)[1].strip())
                    except:
                        pass
                elif line.startswith("懸念スコア:"):
                    try:
                        concern_score = float(line.split(":", 1)[1].strip())
                    except:
                        pass
                elif line.startswith("分析理由:"):
                    analysis_reason = line.split(":", 1)[1].strip()
                    
            return {
                "enthusiasm_score": enthusiasm_score,
                "concern_score": concern_score,
                "analysis_reason": analysis_reason,
                "raw_response": response
            }
            
        except Exception as e:
            print(f"分析エラー: {e}")
            return {
                "enthusiasm_score": 0.5,
                "concern_score": 0.5,
                "analysis_reason": f"分析エラー: {str(e)}",
                "raw_response": response
            }

    def generate_next_action(self, context: EmailGenerationContext) -> Dict[str, str]:
        """次のアクションを提案"""
        
        prompt = f"""候補者の状況を分析して、次に取るべきアクションを提案してください。

候補者: {context.candidate_name}様
企業: {context.company}
職種: {context.job_title}
現在の状況: {context.status}
熱意レベル: {context.enthusiasm_score * 100:.0f}%
懸念レベル: {context.concern_score * 100:.0f}%

状況詳細:
{context.latest_summary}

以下の形式で回答してください：
アクション: [具体的なアクション]
理由: [理由]
優先度: [高/中/低]"""

        response = self._call_ollama(prompt, temperature=0.4, max_tokens=300)
        
        try:
            action = "候補者に連絡を取る"
            reason = "状況を確認するため"
            priority = "中"
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("アクション:"):
                    action = line.split(":", 1)[1].strip()
                elif line.startswith("理由:"):
                    reason = line.split(":", 1)[1].strip()
                elif line.startswith("優先度:"):
                    priority = line.split(":", 1)[1].strip()
                    
            return {
                "action": action,
                "reason": reason,
                "priority": priority,
                "raw_response": response
            }
            
        except Exception as e:
            print(f"アクション生成エラー: {e}")
            return {
                "action": "候補者に連絡を取る",
                "reason": f"エラー: {str(e)}",
                "priority": "中",
                "raw_response": response
            }


# シングルトンインスタンス
llm = QwenLLM() 