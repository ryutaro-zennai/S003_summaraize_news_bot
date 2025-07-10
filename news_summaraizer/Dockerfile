# ベースとなる公式Pythonイメージを指定
FROM python:3.11-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコンテナにコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# スクリプトファイルをコンテナにコピー
COPY summarize_news.py .

# コンテナが実行されたときに実行するコマンドを指定
CMD ["python", "summarize_news.py"]