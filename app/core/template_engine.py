"""
テンプレート提案エンジン
ステータスに応じて適切なメッセージテンプレートを自動提案し、
Qwen3での文章生成をサポートする
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TemplateType(Enum):
    """テンプレートタイプ"""
    INITIAL = "初期段階"
    JOB_RECOMMENDATION = "求人紹介段階"
    APPLICATION = "応募段階"
    DOCUMENT_SCREENING = "書類選考段階"
    INTERVIEW = "面接段階"
    SELECTION = "選考段階"
    OFFER = "内定段階"
    ONBOARDING = "入社準備段階"

@dataclass
class TemplateRecommendation:
    """テンプレート推奨結果"""
    template_name: str
    template_content: str
    relevance_score: float
    reason: str
    sender: str
    receiver: str
    template_type: TemplateType
    customization_hints: List[str]

@dataclass
class StatusContext:
    """ステータスコンテキスト"""
    current_status: str
    candidate_name: str
    company: str
    job_title: str
    enthusiasm_score: float
    concern_score: float
    latest_summary: str
    message_history: List[Dict] = None

class TemplateEngine:
    """テンプレート提案エンジン"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.status_mapping = self._load_status_mapping()
        
    def _load_templates(self) -> Dict[str, str]:
        """抽出されたテンプレートを読み込み"""
        try:
            template_file = Path("extracted_templates.json")
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # フォールバック: デフォルトテンプレート
                return self._get_default_templates()
        except Exception as e:
            print(f"テンプレート読み込みエラー: {e}")
            return self._get_default_templates()
    
    def _load_status_mapping(self) -> Dict[str, List[str]]:
        """ステータスとテンプレートのマッピングを読み込み"""
        try:
            status_file = Path("status_classification.json")
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # available_templatesを抽出
                    mapping = {}
                    for status, info in data.items():
                        mapping[status] = info.get("available_templates", [])
                    return mapping
            else:
                return self._get_default_status_mapping()
        except Exception as e:
            print(f"ステータスマッピング読み込みエラー: {e}")
            return self._get_default_status_mapping()
    
    def _get_default_templates(self) -> Dict[str, str]:
        """デフォルトテンプレート"""
        return {
            "登録お礼": "この度はリクルートエージェントにご登録いただき、ありがとうございます。",
            "求人紹介": "ご条件に合致する求人をご紹介させていただきます。",
            "面接感想依頼": "面接お疲れ様でした。感想をお聞かせください。",
            "内定連絡(CA→CS)": "内定のご連絡をいたします。おめでとうございます。"
        }
    
    def _get_default_status_mapping(self) -> Dict[str, List[str]]:
        """デフォルトステータスマッピング"""
        return {
            "登録完了": ["登録お礼"],
            "求人紹介中": ["求人紹介"],
            "面接完了": ["面接感想依頼"],
            "内定": ["内定連絡(CA→CS)"]
        }
    
    def recommend_templates(self, context: StatusContext) -> List[TemplateRecommendation]:
        """ステータスコンテキストに基づいてテンプレートを推奨"""
        recommendations = []
        
        # 現在のステータスに対応するテンプレートを取得
        applicable_templates = self._get_applicable_templates(context.current_status)
        
        for template_name in applicable_templates:
            if template_name in self.templates:
                template_content = self.templates[template_name]
                
                # 関連性スコアを計算
                relevance_score = self._calculate_relevance_score(
                    template_name, template_content, context
                )
                
                # 推奨理由を生成
                reason = self._generate_recommendation_reason(
                    template_name, context
                )
                
                # 送信者・受信者を判定
                sender, receiver = self._determine_sender_receiver(template_name)
                
                # テンプレートタイプを判定
                template_type = self._determine_template_type(template_name)
                
                # カスタマイズヒントを生成
                customization_hints = self._generate_customization_hints(
                    template_name, context
                )
                
                recommendation = TemplateRecommendation(
                    template_name=template_name,
                    template_content=template_content,
                    relevance_score=relevance_score,
                    reason=reason,
                    sender=sender,
                    receiver=receiver,
                    template_type=template_type,
                    customization_hints=customization_hints
                )
                
                recommendations.append(recommendation)
        
        # スコア順でソート
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations
    
    def _get_applicable_templates(self, status: str) -> List[str]:
        """ステータスに適用可能なテンプレートを取得"""
        # 完全一致を試す
        if status in self.status_mapping:
            return self.status_mapping[status]
        
        # 部分一致を試す
        for mapped_status, templates in self.status_mapping.items():
            if status in mapped_status or mapped_status in status:
                return templates
        
        # キーワードベースのマッチング
        keywords_mapping = {
            "登録": ["登録お礼"],
            "面談": ["面談お礼", "リマインド"],
            "求人": ["求人紹介", "応募書類リマインド"],
            "応募": ["応募お礼"],
            "書類": ["書類通過(CA→CS)", "書類お見送り"],
            "面接": ["面接感想依頼", "日程最終確認(CA→CS)", "面接結果＋日程調整(CA→CS)"],
            "意向": ["意向確認(CA→CS)"],
            "内定": ["内定連絡(CA→CS)", "正式内定ログ(CA→CS)"],
            "退職": ["退職交渉ログ(CA→CS)"]
        }
        
        for keyword, templates in keywords_mapping.items():
            if keyword in status:
                return templates
        
        return []
    
    def _calculate_relevance_score(self, template_name: str, template_content: str, context: StatusContext) -> float:
        """関連性スコアを計算"""
        score = 0.5  # ベーススコア
        
        # ステータスマッチング
        if context.current_status in template_name or template_name in context.current_status:
            score += 0.3
        
        # 熱意・懸念スコアによる調整
        if context.enthusiasm_score > 0.8:
            if "お礼" in template_name or "おめでとう" in template_content:
                score += 0.2
        elif context.enthusiasm_score < 0.5:
            if "確認" in template_name or "依頼" in template_name:
                score += 0.1
        
        if context.concern_score > 0.6:
            if "追加情報" in template_name or "意向確認" in template_name:
                score += 0.2
        
        # メッセージ履歴による調整
        if context.message_history:
            recent_messages = context.message_history[-3:]
            for msg in recent_messages:
                if template_name.lower() in msg.get('subject', '').lower():
                    score -= 0.1  # 最近使用したテンプレートは減点
        
        return min(1.0, max(0.0, score))
    
    def _generate_recommendation_reason(self, template_name: str, context: StatusContext) -> str:
        """推奨理由を生成"""
        reasons = []
        
        # ステータス関連
        if context.current_status in template_name:
            reasons.append(f"現在のステータス「{context.current_status}」に最適")
        
        # スコア関連
        if context.enthusiasm_score > 0.8:
            reasons.append("候補者の熱意が高いため")
        elif context.enthusiasm_score < 0.5:
            reasons.append("候補者の熱意向上が必要なため")
        
        if context.concern_score > 0.6:
            reasons.append("候補者の懸念解消が必要なため")
        
        # テンプレート特性
        if "お礼" in template_name:
            reasons.append("感謝の気持ちを伝える重要なタイミング")
        elif "確認" in template_name:
            reasons.append("状況確認が必要な段階")
        elif "調整" in template_name:
            reasons.append("日程調整が必要な段階")
        
        return "、".join(reasons) if reasons else "標準的な対応として推奨"
    
    def _determine_sender_receiver(self, template_name: str) -> Tuple[str, str]:
        """送信者と受信者を判定"""
        if "CA→CS" in template_name:
            return "CA", "CS"
        elif "CS→CA" in template_name:
            return "CS", "CA"
        elif "RA→CA" in template_name:
            return "RA", "CA"
        elif "CA→RA" in template_name:
            return "CA", "RA"
        else:
            return "CA", "CS"  # デフォルト
    
    def _determine_template_type(self, template_name: str) -> TemplateType:
        """テンプレートタイプを判定"""
        if any(keyword in template_name for keyword in ["登録", "面談", "リマインド"]):
            return TemplateType.INITIAL
        elif any(keyword in template_name for keyword in ["求人", "応募書類"]):
            return TemplateType.JOB_RECOMMENDATION
        elif "応募お礼" in template_name:
            return TemplateType.APPLICATION
        elif "書類" in template_name:
            return TemplateType.DOCUMENT_SCREENING
        elif any(keyword in template_name for keyword in ["面接", "日程"]):
            return TemplateType.INTERVIEW
        elif any(keyword in template_name for keyword in ["意向", "追加情報"]):
            return TemplateType.SELECTION
        elif "内定" in template_name:
            return TemplateType.OFFER
        elif "退職" in template_name:
            return TemplateType.ONBOARDING
        else:
            return TemplateType.INITIAL
    
    def _generate_customization_hints(self, template_name: str, context: StatusContext) -> List[str]:
        """カスタマイズヒントを生成"""
        hints = []
        
        # 候補者名の置換
        hints.append(f"「CS様」を「{context.candidate_name}様」に置換")
        hints.append(f"「●●社」を「{context.company}」に置換")
        hints.append(f"「●●」職種を「{context.job_title}」に置換")
        
        # 状況に応じたヒント
        if context.enthusiasm_score > 0.8:
            hints.append("候補者の熱意が高いため、ポジティブな表現を強調")
        elif context.enthusiasm_score < 0.5:
            hints.append("候補者の熱意向上のため、メリットや魅力を具体的に記載")
        
        if context.concern_score > 0.6:
            hints.append("候補者の懸念があるため、丁寧な説明と配慮を追加")
        
        # テンプレート固有のヒント
        if "日程" in template_name:
            hints.append("具体的な日時候補を複数提示")
        elif "内定" in template_name:
            hints.append("条件詳細と回答期限を明確に記載")
        elif "面接" in template_name:
            hints.append("面接内容と準備事項を具体的に説明")
        
        return hints
    
    def get_template_for_qwen3(self, template_name: str, context: StatusContext) -> str:
        """Qwen3用のテンプレート情報を整形"""
        if template_name not in self.templates:
            return ""
        
        template_content = self.templates[template_name]
        
        # Qwen3用の指示を追加
        qwen3_prompt = f"""
以下のテンプレートを参考に、具体的な状況に合わせてメール文面を生成してください。

【参考テンプレート】
{template_content}

【候補者情報】
- 名前: {context.candidate_name}
- 企業: {context.company}
- 職種: {context.job_title}
- 現在のステータス: {context.current_status}

【状況分析】
- 熱意スコア: {int(context.enthusiasm_score * 100)}%
- 懸念スコア: {int(context.concern_score * 100)}%
- 状況サマリー: {context.latest_summary}

【生成指示】
- テンプレートの構造と文体を参考にしつつ、上記の具体的な情報を反映
- 候補者の熱意や懸念の状況を考慮した適切なトーンに調整
- ●●や○○などのプレースホルダーを実際の情報に置換
- ビジネスメールとして適切な敬語と文体を使用
"""
        
        return qwen3_prompt 