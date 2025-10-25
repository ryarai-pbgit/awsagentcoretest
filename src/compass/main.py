"""
Bedrock AgentCore Starter Toolkit用のエージェント
"""
from bedrock_agentcore import BedrockAgentCoreApp
from agent import ChatAgent

# Bedrock AgentCore アプリケーション
app = BedrockAgentCoreApp()

# グローバルエージェントインスタンス
_agent_instance = None

def get_agent() -> ChatAgent:
    """エージェントインスタンスを取得"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ChatAgent()
    return _agent_instance

@app.entrypoint
def invoke(payload):
    """Bedrock AgentCore用のエントリーポイント"""
    try:
        # エージェントを取得
        agent = get_agent()
        
        # プロンプトを取得
        user_message = payload.get("prompt", "Hello! How can I help you today?")
        
        # エージェントに送信
        result = agent.chat(user_message)
        
        return {"result": result}
        
    except Exception as e:
        return {"error": f"エージェント処理中にエラーが発生しました: {str(e)}"}

def main():
    """対話式のメイン関数"""
    print("🤖 Strands Agent 対話開始（MCPクライアント版）")
    print("=" * 50)
    
    # エージェント初期化
    agent = get_agent()
    
    # エージェント状態確認
    status = agent.get_status()
    print(f"🔗 エージェント状態: {status}")
    print("=" * 50)
    print("💬 チャットを開始します。'exit'または'quit'で終了できます。")
    print("=" * 50)
    
    # 対話ループ
    while True:
        try:
            # ユーザー入力を受け取り
            user_input = input("\n👤 あなた: ").strip()
            
            # 終了条件
            if user_input.lower() in ['exit', 'quit', '終了', 'やめる']:
                print("🤖 エージェント: ありがとうございました。またお会いしましょう！")
                break
            
            # 空の入力はスキップ
            if not user_input:
                continue
            
            # エージェントに送信
            print("🤖 エージェント: 考え中...")
            response = agent.chat(user_input)
            
        except KeyboardInterrupt:
            print("\n\n🤖 エージェント: 中断されました。またお会いしましょう！")
            break
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            print("続行するにはEnterキーを押してください...")
            input()

if __name__ == "__main__":
    app.run()
