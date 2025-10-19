"""
エージェント作成モジュール

このモジュールは、MCPツールを統合したLangChainエージェントを作成します。
ツールの可用性に応じて動的にエージェントを設定し、適切な応答を提供します。
"""

import os
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from .context import Context
from .mcp_tools import MCPToolManager

# システムプロンプトの定義
# LLMがツール使用の判断を行うための指示を含む
SYSTEM_PROMPT = """あなたは日本語で対応するチャットアシスタントです。対応は日本語で行います。

【ツール使用の判断基準】
利用可能なツールがある場合は、以下のルールに従ってください：

1. **一般的な会話・質問**: ツールを使わずに直接応答
   - 挨拶、雑談、一般的な質問
   - 天気、ニュース、一般的な情報
   - プログラミングの一般的な質問

2. **ツールを使用する場合**: 以下の場合のみ
   - ユーザーが明示的にツールの使用を要求した場合
   - 特定のデータ検索や分析が必要な場合
   - ツールの機能に直接関連する質問の場合

【重要な注意事項】
- ツールを呼び出す前に、必要なパラメータがすべて揃っているか確認してください
- 不確実な場合は、ツールを使わずに直接応答してください
- 常に日本語で応答してください

利用可能なツールがない場合は、一般的な質問や会話に直接お答えします。
"""

# エージェントの応答フォーマット定義
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    # A response (always required)
    response: str

def create_my_agent():
    """
    MCPツールを統合したLangChainエージェントを作成・設定する
    
    Returns:
        Agent: 設定済みのLangChainエージェント
        
    Note:
        - MCPツールが利用可能な場合は統合
        - 利用できない場合はツールなしでエージェントを作成
        - LLMがツールの有無を自動的に判断して動作
    """
    # Azure OpenAIモデルの設定
    # 環境変数から設定値を取得してモデルを初期化
    model = init_chat_model(
        "azure_openai:gpt-4o-mini",
        temperature=0.5,  # 創造性と一貫性のバランス
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="gpt-4o-mini",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    )

    # メモリ管理の設定
    # 会話履歴を保持するためのチェックポイント機能
    checkpointer = InMemorySaver()
    
    # MCPツールの初期化と動的取得
    # ツールの可用性に応じてエージェントの設定を決定
    mcp_tool_manager = MCPToolManager()
    mcp_tool_manager.initialize()  # MCPゲートウェイへの接続を試行
    
    # 利用可能なツールを動的に取得
    # ツールが利用できない場合は空のリストが返される
    all_tools = mcp_tool_manager.get_available_tools()
    
    # ツール統合結果の表示
    if all_tools:
        print(f"✅ MCPツールを統合しました: {len(all_tools)}個のツールが利用可能")
    else:
        print("ℹ️ MCPツールが利用できません。一般的なチャットボットとして動作します。")

    # エージェントの作成
    # LLMがツールリストに基づいて自動的にツール使用を判断
    agent = create_agent(
        model=model,                    # 使用するLLMモデル
        system_prompt=SYSTEM_PROMPT,    # システムプロンプト
        tools=all_tools,               # 利用可能なツールリスト（空でも可）
        context_schema=Context,        # コンテキストスキーマ
        response_format=ResponseFormat, # 応答フォーマット
        checkpointer=checkpointer      # メモリ管理
    )
    
    return agent
