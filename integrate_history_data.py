#!/usr/bin/env python3
"""
履歴データ統合スクリプト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from realistic_history_tanaka import tanaka_history
from realistic_history_sato import sato_history
from realistic_history_suzuki import suzuki_history

def integrate_all_history():
    """全候補者の詳細な履歴データを統合"""
    all_history = []
    
    # 田中太郎の履歴 (8件)
    all_history.extend(tanaka_history)
    print(f"田中太郎の履歴: {len(tanaka_history)}件")
    
    # 佐藤花子の履歴 (9件)
    all_history.extend(sato_history)
    print(f"佐藤花子の履歴: {len(sato_history)}件")
    
    # 鈴木一郎の履歴 (10件)
    all_history.extend(suzuki_history)
    print(f"鈴木一郎の履歴: {len(suzuki_history)}件")
    
    print(f"総履歴数: {len(all_history)}件")
    
    # 時系列順にソート
    all_history.sort(key=lambda x: x.timestamp)
    
    return all_history

def generate_demo_main_sample_history():
    """demo_main.py用のsample_message_historyを生成"""
    all_history = integrate_all_history()
    
    # demo_main.py形式で出力
    output = "# 詳細化された履歴データ（実際のビジネステンプレートに基づく）\nsample_message_history = [\n"
    
    for history in all_history:
        output += f"    MessageHistory(\n"
        output += f"        id=\"{history.id}\",\n"
        output += f"        application_id=\"{history.application_id}\",\n"
        output += f"        timestamp=\"{history.timestamp}\",\n"
        output += f"        message_type=\"{history.message_type}\",\n"
        output += f"        sender=\"{history.sender}\",\n"
        output += f"        receiver=\"{history.receiver}\",\n"
        output += f"        subject=\"{history.subject}\",\n"
        output += f"        content=\"\"\"{ history.content.replace('\"\"\"', '\\\"\\\"\\\"')}\"\"\",\n"
        output += f"        is_outbound={history.is_outbound}\n"
        output += f"    ),\n"
    
    output += "]\n"
    
    return output

if __name__ == "__main__":
    print("詳細化された履歴データの統合を開始...")
    
    all_history = integrate_all_history()
    
    print("\n=== 文字数統計 ===")
    total_chars = sum(len(h.content) for h in all_history)
    print(f"総文字数: {total_chars:,}文字")
    print(f"1メッセージ平均: {total_chars // len(all_history):,}文字")
    
    print("\n=== 企業別内訳 ===")
    for app_id in ["app_001", "app_002", "app_003"]:
        app_history = [h for h in all_history if h.application_id == app_id]
        app_chars = sum(len(h.content) for h in app_history)
        candidate_name = "田中太郎" if app_id == "app_001" else "佐藤花子" if app_id == "app_002" else "鈴木一郎"
        print(f"{candidate_name} ({app_id}): {len(app_history)}件, {app_chars:,}文字")
    
    print("\n詳細化された履歴データの統合が完了しました！")
    print("実際のビジネステンプレートの詳細度を反映した内容になっています。") 