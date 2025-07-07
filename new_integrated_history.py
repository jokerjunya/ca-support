# 詳細化された履歴データ（実際のビジネステンプレートに基づく）
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

# 田中太郎の履歴をインポート
from realistic_history_tanaka import tanaka_history

# 佐藤花子の履歴をインポート  
from realistic_history_sato import sato_history

# 鈴木一郎の履歴をインポート
from realistic_history_suzuki import suzuki_history

# 各候補者の履歴を転職途中の段階で制限
# 田中太郎: 書類選考通過後、1次面接前（5件）
# 佐藤花子: 1次面接後、結果待ち（6件）
# 鈴木一郎: 最終面接後、結果待ち（7件）

# 全履歴を統合
all_message_history = []

# 田中太郎の履歴を追加（5件のみ）
for message in tanaka_history[:5]:
    all_message_history.append(message)

# 佐藤花子の履歴を追加（6件のみ）
for message in sato_history[:6]:
    all_message_history.append(message)

# 鈴木一郎の履歴を追加（7件のみ）
for message in suzuki_history[:7]:
    all_message_history.append(message)

# 統計情報を表示
print(f"田中太郎の履歴: {len(tanaka_history[:5])}件")
print(f"佐藤花子の履歴: {len(sato_history[:6])}件")
print(f"鈴木一郎の履歴: {len(suzuki_history[:7])}件")
print(f"総履歴数: {len(all_message_history)}件")

# 各候補者の最新メッセージ内容の確認
print("\n=== 各候補者の最新メッセージ ===")
print(f"田中太郎（最新）: {tanaka_history[4].subject}")
print(f"佐藤花子（最新）: {sato_history[5].subject}")
print(f"鈴木一郎（最新）: {suzuki_history[6].subject}")
print("\n=== 転職途中の段階で停止完了 ===")

# 時系列順にソート
all_message_history.sort(key=lambda x: x.timestamp) 