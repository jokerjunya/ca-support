# 🎯 CA Support System

キャリアアドバイザー向けメール・面談文字起こし自動解析システム

## 🚀 概要

CA Support Systemは、キャリアアドバイザーの業務効率化を目的とした革新的な自動化システムです。メール・面談内容を自動解析し、案件（候補者×求人）単位で最新要約を生成、次にやるべきタスクを自動提案します。

### 🎯 主要機能

- **📧 メール・面談内容の自動解析**
- **📊 案件単位での最新要約生成**
- **🤖 次にやるべきタスクの自動提案**
- **💡 候補者の熱意・懸念スコア算出**
- **📱 美しいダッシュボード**
- **🔮 LLM統合による文面生成（開発予定）**

## 📱 デモサイト

- **🌐 Netlify版**: [https://ca-support-demo.netlify.app](https://ca-support-demo.netlify.app)
- **💻 ローカル版**: `python demo_main.py` で起動

## 🏗️ 技術構成

### Frontend
- **HTML5** + **CSS3** + **JavaScript** (静的版)
- **FastAPI** + **Jinja2** (動的版)
- レスポンシブデザイン対応

### Backend (予定)
- **FastAPI** - REST API
- **SQLModel** - データベースORM
- **OpenAI API** - LLM統合
- **Gmail/Outlook API** - メール取得
- **Zoom/Meet API** - 文字起こし

### Infrastructure
- **Netlify** - 静的サイトホスティング
- **PostgreSQL** - データベース
- **Docker** - コンテナ化

## 🎨 画面構成

### 1. ダッシュボード
- 進行中の案件一覧
- 未完了タスク一覧
- 統計情報表示

### 2. 案件詳細画面
- **ネクストアクション**（最重要機能）
  - 誰にメールを送るか
  - どんな内容を送るか
  - 件名・本文テンプレート
- **履歴タイムライン**
  - メール送受信履歴
  - 面談記録
  - システム通知

### 3. 候補者詳細画面（開発予定）
- 候補者の全案件一覧
- 総合評価・スコア

## 🚀 クイックスタート

### ローカル環境で起動

```bash
# リポジトリのクローン
git clone https://github.com/jokerjunya/ca-support.git
cd ca-support

# 仮想環境の作成・有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements-minimal.txt

# デモ版の起動
python demo_main.py
```

### アクセス先
- **ダッシュボード**: http://localhost:8000/dashboard
- **案件詳細**: http://localhost:8000/application/app_001
- **API ドキュメント**: http://localhost:8000/docs

## 📊 サンプルデータ

### 候補者
- **田中太郎** - ABC株式会社 → Acme株式会社 (シニアエンジニア)
- **佐藤花子** - XYZ株式会社 → Tech Corp (プロダクトマネージャー)
- **鈴木一郎** - DEF株式会社 → StartUp Inc (フロントエンドエンジニア)

### 主要機能のデモ
- 📧 **メール送信レコメンド**: CS宛て面接候補日提示
- 🤖 **AI文面生成**: 将来LLM統合で自動生成
- 📜 **履歴管理**: メール・面談・システム通知を時系列表示

## 🔮 開発ロードマップ

### フェーズ1: 基盤構築 ✅
- [x] プロジェクト構造作成
- [x] データベースモデル設計
- [x] FastAPI基本構造
- [x] 美しいダッシュボードUI
- [x] 案件詳細画面
- [x] Netlify対応

### フェーズ2: データ取得・解析 🔄
- [ ] Gmail/Outlook API統合
- [ ] Zoom/Meet文字起こし取得
- [ ] AI解析パイプライン
- [ ] 候補者詳細画面

### フェーズ3: LLM統合 🔮
- [ ] OpenAI API統合
- [ ] メール文面自動生成
- [ ] コンテキスト分析
- [ ] 送信先自動判定

### フェーズ4: 本格運用 📈
- [ ] Slack通知連携
- [ ] パフォーマンス最適化
- [ ] セキュリティ強化
- [ ] 本番環境構築

## 🎯 システム設計思想

### 統合可能性を重視
現在はルールベースのシンプルなレコメンドですが、将来のLLM統合を見据えた設計：

```python
class NextAction:
    action_type: str        # "send_email", "schedule_call"
    target_person: str      # "CS", "candidate", "RA"
    message_template: str   # 基本テンプレート
    ai_suggested_content: str  # LLM生成文面（将来追加）
    priority: str
    due_date: str
```

### 実用性優先
CAの実際の業務フローを重視：
- **ネクストアクション最優先表示**
- **誰に何を送るかまで明確化**
- **ワンクリックでメール送信**
- **履歴の完全可視化**

## 🤝 貢献

プロジェクトへの貢献を歓迎します！

1. Fork このリポジトリ
2. Feature ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチをプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Request を作成

## 📝 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。

## 📞 お問い合わせ

質問やフィードバックがございましたら、お気軽にお問い合わせください。

- **GitHub Issues**: [Issues](https://github.com/jokerjunya/ca-support/issues)
- **Email**: [連絡先メールアドレス]

---

**🎯 CA Support System** - キャリアアドバイザーの業務を革新する自動化システム 