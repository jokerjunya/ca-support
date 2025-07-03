FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムパッケージの更新とインストール
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポートの公開
EXPOSE 8000

# アプリケーションの実行
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 