FROM python:3.11-slim

WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app.py .

# ポート8000を公開
EXPOSE 8000

# FastAPIアプリを起動
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
