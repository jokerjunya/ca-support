# 完全な履歴データ（CA-RA間の内部連絡を含む）
from pydantic import BaseModel
from datetime import datetime

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

# 既存の履歴データをインポート
from new_integrated_history import all_message_history as existing_history

# CA-RA間の内部連絡をインポート
from ca_ra_internal_messages import ca_ra_internal_messages

# 全履歴を統合
all_message_history = []

# 既存の履歴を追加
for message in existing_history:
    all_message_history.append(message)

# CA-RA間の内部連絡を追加
for message in ca_ra_internal_messages:
    all_message_history.append(message)

# 時系列順にソート
all_message_history.sort(key=lambda x: x.timestamp)

# 統計情報を表示
print(f"既存の履歴: {len(existing_history)}件")
print(f"CA-RA間の内部連絡: {len(ca_ra_internal_messages)}件")
print(f"完全な履歴: {len(all_message_history)}件")

# 各候補者の履歴件数を確認
tanaka_count = len([m for m in all_message_history if m.application_id == "app_001"])
sato_count = len([m for m in all_message_history if m.application_id == "app_002"])
suzuki_count = len([m for m in all_message_history if m.application_id == "app_003"])

print(f"\n=== 候補者別の履歴数 ===")
print(f"田中太郎 (app_001): {tanaka_count}件")
print(f"佐藤花子 (app_002): {sato_count}件")
print(f"鈴木一郎 (app_003): {suzuki_count}件")

# 内部連絡の統計
internal_messages = [m for m in all_message_history if m.message_type == "internal_note"]
ca_to_ra = len([m for m in internal_messages if m.sender == "CA" and m.receiver == "RA"])
ra_to_ca = len([m for m in internal_messages if m.sender == "RA" and m.receiver == "CA"])

print(f"\n=== 内部連絡の統計 ===")
print(f"CA→RA: {ca_to_ra}件")
print(f"RA→CA: {ra_to_ca}件")
print(f"内部連絡総数: {len(internal_messages)}件")

# 時系列の確認（直近10件）
print(f"\n=== 直近10件の履歴 ===")
for message in all_message_history[-10:]:
    print(f"{message.timestamp}: {message.sender}→{message.receiver} | {message.subject[:50]}...")

print(f"\n=== 完全な履歴データ統合完了 ===") 