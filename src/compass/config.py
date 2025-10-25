"""
設定ファイル
"""
import os

# AWS AgentCore Gateway設定
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = os.getenv("TOKEN_URL")
GATEWAY_URL = os.getenv("GATEWAY_URL")

# Gemini API設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# システムプロンプト
SYSTEM_PROMPT = """あなたは日本語で対応するチャットアシスタントです。

【機能】
- 一般的な会話や質問に日本語で応答
- 利用可能なツールを動的に発見・使用
- データ分析、検索、その他のタスクを適切なツールで実行

【ツール使用方針】
- ユーザーの要求に応じて、利用可能なツールから最適なものを選択
- ツールの実行結果を分かりやすく日本語で説明
- ツールが利用できない場合は、一般的な回答を提供

【応答方針】
- 常に日本語で応答
- ツールの実行結果は分かりやすく説明
- エラーが発生した場合は適切に説明
"""
