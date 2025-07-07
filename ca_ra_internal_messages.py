# CA-RA間の内部連絡履歴（extracted_templates.jsonの実際のテンプレートに基づく）
from pydantic import BaseModel

class MessageHistory(BaseModel):
    id: str
    application_id: str
    timestamp: str
    message_type: str
    sender: str
    receiver: str
    subject: str
    content: str
    is_outbound: bool

# CA-RA間の内部連絡（実際のテンプレートベース）
ca_ra_internal_messages = [
    # 田中太郎案件: 書類選考通過の内部連絡
    MessageHistory(
        id="internal_tanaka_001",
        application_id="app_001",
        timestamp="2024-12-04 10:30:00",
        message_type="internal_note",
        sender="RA",
        receiver="CA",
        subject="【書類選考通過】田中太郎さん - Acme株式会社 1次面接調整のお願い",
        content="""■RAからの伝言
お疲れ様です。RAです。

書類選考通過です。一次調整お願いいたします。

※企業指定の日程ではございませんので、
ご都合が合わない場合は別日で幅広くいただけますと幸いです。

※先の日程やピンポイント日程の場合は
【開示できる内容で】理由のご記載お願いいたします。
記載のない場合は、差し戻し対応とさせていただきます。

＝＝＝＝求職者向けメール 件名＝＝＝＝＝
【ご対応願】Acme株式会社：1次面接 選考日程調整のご連絡

【企業名】Acme株式会社
【希望日時】
2024/12/10(火) 10:00スタート～18:00スタートの間
2024/12/11(水) 10:00スタート～18:00スタートの間
2024/12/12(木) 10:00スタート～18:00スタートの間
【所要時間】
約1時間0分

よろしくお願いいたします。""",
        is_outbound=False
    ),
    
    # 田中太郎案件: 候補日返信
    MessageHistory(
        id="internal_tanaka_002",
        application_id="app_001",
        timestamp="2024-12-04 16:45:00",
        message_type="internal_note",
        sender="CA",
        receiver="RA",
        subject="【候補日返信】田中太郎さん - Acme株式会社 1次面接日程",
        content="""※候補者のPDT入力内容から自動生成して送信されています。
候補者が希望日程を入力しました。企業側との調整をお願いいたします。

【候補者】田中太郎さん
【候補者の希望日程(企業が提示した候補日程内)】
2024/12/10(火) 14:00スタート～16:00スタートの間
2024/12/11(水) 10:00スタート～12:00スタートの間""",
        is_outbound=True
    ),
    
    # 佐藤花子案件: 書類選考通過の内部連絡
    MessageHistory(
        id="internal_sato_001",
        application_id="app_002",
        timestamp="2024-11-28 11:20:00",
        message_type="internal_note",
        sender="RA",
        receiver="CA",
        subject="【書類選考通過】佐藤花子さん - Tech Innovation株式会社 1次面接調整のお願い",
        content="""■RAからの伝言
お疲れ様です。RAです。

書類選考通過です。一次調整お願いいたします。

※企業指定の日程ではございませんので、
ご都合が合わない場合は別日で幅広くいただけますと幸いです。

【企業名】Tech Innovation株式会社
【希望日時】
2024/12/03(火) 10:00スタート～18:00スタートの間
2024/12/04(水) 10:00スタート～18:00スタートの間
2024/12/05(木) 10:00スタート～18:00スタートの間
【所要時間】
約1時間30分

よろしくお願いいたします。""",
        is_outbound=False
    ),
    
    # 佐藤花子案件: 追加情報依頼
    MessageHistory(
        id="internal_sato_002",
        application_id="app_002",
        timestamp="2024-12-06 09:15:00",
        message_type="internal_note",
        sender="RA",
        receiver="CA",
        subject="【追加情報依頼】佐藤花子さん - Tech Innovation株式会社 技術スキル詳細確認",
        content="""CAさん
お疲れ様です。RAです。

Tech Innovation株式会社選考中の佐藤花子さんの件でご連絡です。
企業より下記ご確認頂戴いたしました。

=
１，現年収・希望年収(下限含む)のご教示をお願いいたします。
２，チームマネジメント経験の具体的な詳細をお聞かせください。
　　- 管理していたチームの規模
　　- プロジェクトマネジメントの手法
　　- 技術選定の経験
３，VPoE候補としての今後のキャリアビジョンについて

お忙しいところ恐れ入りますが、佐藤さんへのご確認をお願いいたします。

=
【12/9(月)正午〆】
お忙しいところ恐縮ですが上記期日までにご確認をお願いいたします。
よろしくお願いいたします。""",
        is_outbound=False
    ),
    
    # 佐藤花子案件: 追加情報返信
    MessageHistory(
        id="internal_sato_003",
        application_id="app_002",
        timestamp="2024-12-09 10:30:00",
        message_type="internal_note",
        sender="CA",
        receiver="RA",
        subject="【追加情報返信】佐藤花子さん - Tech Innovation株式会社 技術スキル詳細",
        content="""RAさん
お疲れ様です。CAです。

ご本人から回答をいただきましたので共有いたします。
以下、ご本人からの回答です。

=
１，現年収・希望年収について
現年収: 950万円
希望年収: 1,200万円
下限の希望年収: 1,050万円

２，チームマネジメント経験について
- 管理していたチームの規模: エンジニア15名（フロントエンド7名、バックエンド8名）
- プロジェクトマネジメントの手法: アジャイル開発（スクラム）を採用、2週間スプリント
- 技術選定の経験: React.js、Node.js、PostgreSQLの技術スタック選定から導入まで担当

３，VPoE候補としての今後のキャリアビジョン
技術組織の成長を支援し、エンジニアが最大限のパフォーマンスを発揮できる環境構築を目指します。
特に、技術的な意思決定とビジネス成果の橋渡し役として、スケーラブルな組織作りに貢献したいと考えております。

=
どうぞよろしくお願いいたします。""",
        is_outbound=True
    ),
    
    # 鈴木一郎案件: 意向確認接続
    MessageHistory(
        id="internal_suzuki_001",
        application_id="app_003",
        timestamp="2024-12-12 14:20:00",
        message_type="internal_note",
        sender="CA",
        receiver="RA",
        subject="【意向確認接続】鈴木一郎さん - Design Works株式会社 最終面接後の意向",
        content="""担当RA/RAサポさん
お疲れ様です。

ご本人から回答をいただきましたので共有いたします。
以下、ご本人からの回答です。

=
━━━━━━━━━━━━━━━━
【注意】
＜企業依頼＞
現時点での弊社に対する点数(6点/10点満点中)

・希望年収：720万円
・最低希望年収ライン：650万円
・入社可能日（最短）：2025/02/01(土)
・就職活動の状況（当社の志望度も含めて）：第一志望候補だが、他社の条件と比較検討中

■内定が出た場合、内定をご承諾いただけるか
C：優先順位が同程度の併願企業があるため悩んでいる（60％程度の温度感）

■現時点での企業に対しての懸念事項
年収面:
・提示される年収が現年収（650万円）と比較して大幅な向上が見込めるか不安
・デザイナーとしてのキャリアパスが明確でない

■どういった情報があればご入社を前向きに検討いただけそうでしょうか
・具体的な年収提示額
・デザイナーのキャリアパス詳細
・チームの構成とデザイン業務の裁量範囲

■他チャンネルを含めた進捗状況
Creative Agency A社：最終面接完了、結果待ち 第一志望
Startup B社：2次面接予定 第二志望

■転職で一番大切にしている点
・デザイナーとしてのスキル向上機会
・クリエイティブな環境での仕事
・適正な評価と報酬

■退職交渉に必要な期間
約1.5ヶ月（引き継ぎ期間含む）
━━━━━━━━━━━━━━━━
=

※併願企業名が記載されている場合、企業名は伏せて連携いただくようお願いします。
企業には業界や選考フェーズでご連携ください。

どうぞよろしくお願いいたします。""",
        is_outbound=True
    ),
    
    # 鈴木一郎案件: 面接感想連携（RAからCAへの内部連絡）
    MessageHistory(
        id="internal_suzuki_002",
        application_id="app_003",
        timestamp="2024-12-15 16:10:00",
        message_type="internal_note",
        sender="RA",
        receiver="CA",
        subject="【面接感想連携】鈴木一郎さん - Design Works株式会社 最終面接フィードバック",
        content="""以下の面接感想について、CAから連携されました。

【面接日時】 2024/12/15 14:00
【面接区分】 最終面接
【企業名】 Design Works株式会社
【仕事の名称】 【シニアデザイナー】UI/UXデザイン リード候補

面接感想一覧・詳細画面より、面接感想をご確認いただき、
必要に応じて、各項目の文面編集・企業向けの連携対象を設定の上、企業宛に面接感想を連携してください。

【面接感想ID】DW_20241215_001

■企業への連携内容（要約）
・デザイン業務への熱意は高く評価
・チームリーダーとしての経験も豊富
・ただし年収面での調整が必要
・他社との比較検討中のため、条件面での魅力的な提示が重要

よろしくお願いいたします。""",
        is_outbound=False
    )
]

# 統計情報
print(f"CA-RA間の内部連絡数: {len(ca_ra_internal_messages)}件")
print("\n=== 追加される内部連絡 ===")
for msg in ca_ra_internal_messages:
    print(f"- {msg.sender}→{msg.receiver}: {msg.subject}")
print(f"\n新しい総履歴数: {18 + len(ca_ra_internal_messages)}件") 