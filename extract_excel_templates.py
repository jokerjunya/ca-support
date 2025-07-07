import pandas as pd
import openpyxl
from pathlib import Path
import json
import re

def extract_excel_templates(file_path):
    """
    エクセルファイルからフェーズ別テンプレートメッセージを抽出する
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"ファイルが見つかりません: {file_path}")
        return
    
    print(f"📄 エクセルファイル読み込み中: {file_path}")
    
    # openpyxlを使用してシート情報を取得
    wb = openpyxl.load_workbook(file_path)
    sheet_names = wb.sheetnames
    
    print(f"📋 シート数: {len(sheet_names)}")
    print(f"📋 シート名: {sheet_names}")
    
    templates = {}
    
    for sheet_name in sheet_names:
        print(f"\n🔍 シート「{sheet_name}」を処理中...")
        
        # pandasでエクセルを読み込み
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            print(f"   📊 シートサイズ: {df.shape[0]} 行 x {df.shape[1]} 列")
            
            # データを抽出してテキストを結合
            template_text = extract_template_from_sheet(df, sheet_name)
            
            if template_text:
                templates[sheet_name] = template_text
                print(f"   ✅ テンプレート抽出完了: {len(template_text)} 文字")
            else:
                print(f"   ❌ テンプレート抽出失敗")
                
        except Exception as e:
            print(f"   ❌ エラー: {e}")
    
    # 結果を保存
    save_templates(templates)
    
    return templates

def extract_template_from_sheet(df, sheet_name):
    """
    個別シートからテンプレートテキストを抽出
    """
    template_lines = []
    
    # NaNを空文字に置換
    df = df.fillna('')
    
    # 各行を処理
    for index, row in df.iterrows():
        # 行の中の全ての列を結合
        row_text = ''
        for col in df.columns:
            cell_value = str(row[col]).strip()
            if cell_value and cell_value != 'nan':
                row_text += cell_value + ' '
        
        row_text = row_text.strip()
        
        # 空の行や意味のない行をスキップ
        if row_text and len(row_text) > 1:
            # 特殊文字の処理
            row_text = clean_text(row_text)
            template_lines.append(row_text)
    
    # 全ての行を結合
    template_text = '\n'.join(template_lines)
    
    return template_text

def clean_text(text):
    """
    テキストのクリーニング
    """
    # 不要な文字や記号を削除
    text = re.sub(r'=+', '=', text)  # 連続する=を1つに
    text = re.sub(r'\s+', ' ', text)  # 連続する空白を1つに
    text = text.strip()
    
    return text

def save_templates(templates):
    """
    抽出したテンプレートを保存
    """
    # JSONファイルとして保存
    with open('extracted_templates.json', 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    # 読みやすいテキストファイルとして保存
    with open('extracted_templates.txt', 'w', encoding='utf-8') as f:
        f.write("# エクセルファイルから抽出したフェーズ別テンプレートメッセージ\n")
        f.write("=" * 60 + "\n\n")
        
        for sheet_name, template in templates.items():
            f.write(f"## {sheet_name}\n")
            f.write("-" * 40 + "\n")
            f.write(template)
            f.write("\n\n" + "=" * 60 + "\n\n")
    
    print(f"\n💾 テンプレートを保存しました:")
    print(f"   📁 JSON: extracted_templates.json")
    print(f"   📁 テキスト: extracted_templates.txt")

if __name__ == "__main__":
    # エクセルファイルのパス
    excel_file = "/Users/01062544/Downloads/202507_シーケンス図（CA業務）.xlsx"
    
    # テンプレートを抽出
    templates = extract_excel_templates(excel_file)
    
    # 結果を表示
    print("\n📋 抽出結果サマリー:")
    for sheet_name, template in templates.items():
        print(f"   🔖 {sheet_name}: {len(template)} 文字") 