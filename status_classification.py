"""
CA業務シーケンス図に基づくステータス分類とネクストアクション設計
"""

from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

class ApplicationStatus(Enum):
    """案件のステータス"""
    # 初期段階
    REGISTERED = "登録完了"
    INTERVIEW_SCHEDULED = "面談予定"
    INTERVIEW_COMPLETED = "面談完了"
    
    # 求人紹介・応募段階
    JOB_RECOMMENDED = "求人紹介中"
    APPLICATION_SUBMITTED = "応募済み"
    DOCUMENT_UNDER_REVIEW = "書類選考中"
    
    # 書類選考結果
    DOCUMENT_PASSED = "書類通過"
    DOCUMENT_REJECTED = "書類不合格"
    
    # 面接段階
    INTERVIEW_SCHEDULING = "面接日程調整中"
    INTERVIEW_SCHEDULED_COMPANY = "面接予定"
    INTERVIEW_COMPLETED_COMPANY = "面接完了"
    INTERVIEW_FEEDBACK_PENDING = "面接感想待ち"
    
    # 選考結果・意向確認
    INTERVIEW_PASSED = "面接通過"
    INTERVIEW_REJECTED = "面接不合格"
    INTENTION_CONFIRMATION = "意向確認中"
    ADDITIONAL_INFO_REQUESTED = "追加情報依頼中"
    
    # 内定段階
    OFFER_RECEIVED = "内定通知"
    OFFER_CONSIDERATION = "内定検討中"
    OFFER_ACCEPTED = "内定承諾"
    OFFER_REJECTED = "内定辞退"
    
    # 入社準備段階
    RESIGNATION_NEGOTIATION = "退職交渉中"
    RESIGNATION_COMPLETED = "退職完了"
    ONBOARDING_PREPARATION = "入社準備中"
    ONBOARDING_COMPLETED = "入社完了"

class ParticipantRole(Enum):
    """参加者の役割"""
    CS = "候補者"
    CA = "キャリアアドバイザー"
    RA = "リクルーティングアドバイザー"

@dataclass
class MessageTemplate:
    """メッセージテンプレート"""
    template_id: str
    name: str
    content: str
    sender: ParticipantRole
    receiver: ParticipantRole
    applicable_statuses: List[ApplicationStatus]
    
@dataclass
class NextAction:
    """ネクストアクション"""
    action_id: str
    description: str
    responsible_role: ParticipantRole
    deadline_days: Optional[int] = None
    required_info: List[str] = None
    
@dataclass
class StatusClassification:
    """ステータス分類"""
    status: ApplicationStatus
    description: str
    phase: str
    possible_next_statuses: List[ApplicationStatus]
    required_actions: List[NextAction]
    available_templates: List[str]

class CAWorkflowClassifier:
    """CA業務ワークフロー分類器"""
    
    def __init__(self):
        self.status_classifications = self._initialize_status_classifications()
        self.message_templates = self._initialize_message_templates()
        
    def _initialize_status_classifications(self) -> Dict[ApplicationStatus, StatusClassification]:
        """ステータス分類の初期化"""
        return {
            # 初期段階
            ApplicationStatus.REGISTERED: StatusClassification(
                status=ApplicationStatus.REGISTERED,
                description="サービス登録完了、面談予定調整中",
                phase="初期段階",
                possible_next_statuses=[ApplicationStatus.INTERVIEW_SCHEDULED],
                required_actions=[
                    NextAction("schedule_interview", "面談日程調整", ParticipantRole.CA, 3),
                    NextAction("send_reminder", "リマインド送信", ParticipantRole.CA, 1)
                ],
                available_templates=["登録お礼", "リマインド"]
            ),
            
            ApplicationStatus.INTERVIEW_COMPLETED: StatusClassification(
                status=ApplicationStatus.INTERVIEW_COMPLETED,
                description="面談完了、求人紹介準備中",
                phase="初期段階",
                possible_next_statuses=[ApplicationStatus.JOB_RECOMMENDED],
                required_actions=[
                    NextAction("send_interview_thanks", "面談お礼送信", ParticipantRole.CA, 1),
                    NextAction("recommend_jobs", "求人紹介", ParticipantRole.CA, 3)
                ],
                available_templates=["面談お礼", "求人紹介"]
            ),
            
            # 求人紹介・応募段階
            ApplicationStatus.JOB_RECOMMENDED: StatusClassification(
                status=ApplicationStatus.JOB_RECOMMENDED,
                description="求人紹介済み、応募意思確認中",
                phase="求人紹介段階",
                possible_next_statuses=[ApplicationStatus.APPLICATION_SUBMITTED],
                required_actions=[
                    NextAction("confirm_application", "応募意思確認", ParticipantRole.CA, 3),
                    NextAction("document_reminder", "応募書類リマインド", ParticipantRole.CA, 5)
                ],
                available_templates=["求人紹介", "応募書類リマインド"]
            ),
            
            ApplicationStatus.APPLICATION_SUBMITTED: StatusClassification(
                status=ApplicationStatus.APPLICATION_SUBMITTED,
                description="応募完了、書類選考中",
                phase="応募段階",
                possible_next_statuses=[ApplicationStatus.DOCUMENT_PASSED, ApplicationStatus.DOCUMENT_REJECTED],
                required_actions=[
                    NextAction("send_application_thanks", "応募お礼送信", ParticipantRole.CA, 1),
                    NextAction("follow_up_screening", "書類選考状況確認", ParticipantRole.RA, 7)
                ],
                available_templates=["応募お礼"]
            ),
            
            # 書類選考結果
            ApplicationStatus.DOCUMENT_PASSED: StatusClassification(
                status=ApplicationStatus.DOCUMENT_PASSED,
                description="書類選考通過、面接日程調整中",
                phase="書類選考段階",
                possible_next_statuses=[ApplicationStatus.INTERVIEW_SCHEDULED_COMPANY],
                required_actions=[
                    NextAction("notify_document_pass", "書類通過通知", ParticipantRole.CA, 1),
                    NextAction("schedule_interview_company", "面接日程調整", ParticipantRole.RA, 3)
                ],
                available_templates=["書類通過(CA→CS)", "書類通過(RA→CA)"]
            ),
            
            ApplicationStatus.DOCUMENT_REJECTED: StatusClassification(
                status=ApplicationStatus.DOCUMENT_REJECTED,
                description="書類選考不合格、他の求人検討",
                phase="書類選考段階",
                possible_next_statuses=[ApplicationStatus.JOB_RECOMMENDED],
                required_actions=[
                    NextAction("notify_document_reject", "書類不合格通知", ParticipantRole.CA, 1),
                    NextAction("recommend_alternative_jobs", "代替求人紹介", ParticipantRole.CA, 3)
                ],
                available_templates=["書類お見送り"]
            ),
            
            # 面接段階
            ApplicationStatus.INTERVIEW_SCHEDULING: StatusClassification(
                status=ApplicationStatus.INTERVIEW_SCHEDULING,
                description="面接日程調整中",
                phase="面接段階",
                possible_next_statuses=[ApplicationStatus.INTERVIEW_SCHEDULED_COMPANY],
                required_actions=[
                    NextAction("confirm_interview_schedule", "面接日程最終確認", ParticipantRole.CA, 2),
                    NextAction("send_schedule_fix", "日程確定通知", ParticipantRole.CA, 1)
                ],
                available_templates=["日程最終確認(CA→CS)", "日程最終確認(RA→CA)", "日程FIX連絡"]
            ),
            
            ApplicationStatus.INTERVIEW_COMPLETED_COMPANY: StatusClassification(
                status=ApplicationStatus.INTERVIEW_COMPLETED_COMPANY,
                description="面接完了、感想・結果待ち",
                phase="面接段階",
                possible_next_statuses=[ApplicationStatus.INTERVIEW_PASSED, ApplicationStatus.INTERVIEW_REJECTED],
                required_actions=[
                    NextAction("request_interview_feedback", "面接感想依頼", ParticipantRole.CA, 1),
                    NextAction("follow_up_interview_result", "面接結果確認", ParticipantRole.RA, 3)
                ],
                available_templates=["面接感想依頼", "面接感想連携"]
            ),
            
            # 選考結果・意向確認
            ApplicationStatus.INTERVIEW_PASSED: StatusClassification(
                status=ApplicationStatus.INTERVIEW_PASSED,
                description="面接通過、次回面接または意向確認",
                phase="選考段階",
                possible_next_statuses=[ApplicationStatus.INTERVIEW_SCHEDULED_COMPANY, ApplicationStatus.INTENTION_CONFIRMATION],
                required_actions=[
                    NextAction("notify_interview_pass", "面接通過通知", ParticipantRole.CA, 1),
                    NextAction("schedule_next_interview", "次回面接調整", ParticipantRole.RA, 3)
                ],
                available_templates=["面接結果＋日程調整(CA→CS)"]
            ),
            
            ApplicationStatus.INTENTION_CONFIRMATION: StatusClassification(
                status=ApplicationStatus.INTENTION_CONFIRMATION,
                description="意向確認中",
                phase="選考段階",
                possible_next_statuses=[ApplicationStatus.OFFER_RECEIVED, ApplicationStatus.ADDITIONAL_INFO_REQUESTED],
                required_actions=[
                    NextAction("request_intention", "意向確認依頼", ParticipantRole.CA, 2),
                    NextAction("share_intention_result", "意向確認結果共有", ParticipantRole.RA, 1)
                ],
                available_templates=["意向確認(CA→CS)", "意向確認返信(CS→CA)", "意向確認接続(CA→RA)"]
            ),
            
            ApplicationStatus.ADDITIONAL_INFO_REQUESTED: StatusClassification(
                status=ApplicationStatus.ADDITIONAL_INFO_REQUESTED,
                description="追加情報依頼中",
                phase="選考段階",
                possible_next_statuses=[ApplicationStatus.INTENTION_CONFIRMATION],
                required_actions=[
                    NextAction("request_additional_info", "追加情報依頼", ParticipantRole.CA, 2),
                    NextAction("share_additional_info", "追加情報共有", ParticipantRole.RA, 1)
                ],
                available_templates=["追加情報依頼(CA→CS)", "追加情報依頼(RA→CA)", "追加情報返信(CA→RA)", "追加情報返信(CS→CA)"]
            ),
            
            # 内定段階
            ApplicationStatus.OFFER_RECEIVED: StatusClassification(
                status=ApplicationStatus.OFFER_RECEIVED,
                description="内定通知、検討中",
                phase="内定段階",
                possible_next_statuses=[ApplicationStatus.OFFER_ACCEPTED, ApplicationStatus.OFFER_REJECTED],
                required_actions=[
                    NextAction("notify_offer", "内定通知", ParticipantRole.CA, 1),
                    NextAction("follow_up_offer_decision", "内定回答確認", ParticipantRole.CA, 3)
                ],
                available_templates=["内定連絡(CA→CS)", "内定連絡(RA→CA)"]
            ),
            
            ApplicationStatus.OFFER_ACCEPTED: StatusClassification(
                status=ApplicationStatus.OFFER_ACCEPTED,
                description="内定承諾、退職交渉開始",
                phase="内定段階",
                possible_next_statuses=[ApplicationStatus.RESIGNATION_NEGOTIATION],
                required_actions=[
                    NextAction("process_offer_acceptance", "内定承諾手続き", ParticipantRole.CA, 1),
                    NextAction("start_resignation_support", "退職交渉サポート開始", ParticipantRole.CA, 3)
                ],
                available_templates=["正式内定ログ(CA→CS)", "内定受諾(CS→CA)", "内定受諾(CA→RA)"]
            ),
            
            # 入社準備段階
            ApplicationStatus.RESIGNATION_NEGOTIATION: StatusClassification(
                status=ApplicationStatus.RESIGNATION_NEGOTIATION,
                description="退職交渉中",
                phase="入社準備段階",
                possible_next_statuses=[ApplicationStatus.RESIGNATION_COMPLETED],
                required_actions=[
                    NextAction("support_resignation", "退職交渉サポート", ParticipantRole.CA, 7),
                    NextAction("confirm_resignation_status", "退職状況確認", ParticipantRole.CA, 3)
                ],
                available_templates=["退職交渉ログ(CA→CS)", "退職交渉ログ(CS→CA)", "退職交渉ログ(CA→RA)"]
            ),
            
            ApplicationStatus.RESIGNATION_COMPLETED: StatusClassification(
                status=ApplicationStatus.RESIGNATION_COMPLETED,
                description="退職完了、入社準備中",
                phase="入社準備段階",
                possible_next_statuses=[ApplicationStatus.ONBOARDING_COMPLETED],
                required_actions=[
                    NextAction("confirm_onboarding", "入社準備確認", ParticipantRole.CA, 5),
                    NextAction("final_support", "最終サポート", ParticipantRole.CA, 1)
                ],
                available_templates=[]
            )
        }
    
    def _initialize_message_templates(self) -> Dict[str, MessageTemplate]:
        """メッセージテンプレートの初期化"""
        # 実際の抽出データを使用して初期化
        return {}
    
    def get_status_classification(self, status: ApplicationStatus) -> StatusClassification:
        """ステータス分類を取得"""
        return self.status_classifications.get(status)
    
    def get_available_templates(self, status: ApplicationStatus) -> List[str]:
        """利用可能なテンプレートを取得"""
        classification = self.get_status_classification(status)
        return classification.available_templates if classification else []
    
    def get_next_actions(self, status: ApplicationStatus) -> List[NextAction]:
        """ネクストアクションを取得"""
        classification = self.get_status_classification(status)
        return classification.required_actions if classification else []
    
    def get_possible_next_statuses(self, status: ApplicationStatus) -> List[ApplicationStatus]:
        """可能な次のステータスを取得"""
        classification = self.get_status_classification(status)
        return classification.possible_next_statuses if classification else []
    
    def export_classification_data(self, filename: str = "status_classification.json"):
        """分類データをJSONでエクスポート"""
        data = {}
        for status, classification in self.status_classifications.items():
            data[status.value] = {
                "description": classification.description,
                "phase": classification.phase,
                "possible_next_statuses": [s.value for s in classification.possible_next_statuses],
                "required_actions": [
                    {
                        "action_id": action.action_id,
                        "description": action.description,
                        "responsible_role": action.responsible_role.value,
                        "deadline_days": action.deadline_days,
                        "required_info": action.required_info or []
                    }
                    for action in classification.required_actions
                ],
                "available_templates": classification.available_templates
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"ステータス分類データを {filename} に保存しました。")

def main():
    """メイン実行"""
    classifier = CAWorkflowClassifier()
    
    # ステータス分類の表示
    print("=" * 60)
    print("CA業務ワークフロー ステータス分類")
    print("=" * 60)
    
    current_phase = ""
    for status, classification in classifier.status_classifications.items():
        if classification.phase != current_phase:
            current_phase = classification.phase
            print(f"\n【{current_phase}】")
            print("-" * 40)
        
        print(f"\n🔸 {status.value}")
        print(f"   説明: {classification.description}")
        print(f"   次のステータス: {[s.value for s in classification.possible_next_statuses]}")
        print(f"   必要なアクション: {len(classification.required_actions)}個")
        print(f"   利用可能テンプレート: {len(classification.available_templates)}個")
        
        if classification.required_actions:
            print("   【必要なアクション】")
            for action in classification.required_actions:
                deadline = f"({action.deadline_days}日以内)" if action.deadline_days else ""
                print(f"     - {action.description} [{action.responsible_role.value}] {deadline}")
        
        if classification.available_templates:
            print("   【利用可能テンプレート】")
            for template in classification.available_templates:
                print(f"     - {template}")
    
    # 分類データをエクスポート
    classifier.export_classification_data()

if __name__ == "__main__":
    main() 