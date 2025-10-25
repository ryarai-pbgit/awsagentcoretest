"""
Strands Agent実装
"""
from typing import Dict, Any, List
from strands import Agent
from strands.models.gemini import GeminiModel
from strands.tools.mcp.mcp_client import MCPClient

from config import CLIENT_ID, CLIENT_SECRET, TOKEN_URL, GATEWAY_URL, GEMINI_API_KEY, SYSTEM_PROMPT
from utils import fetch_access_token, create_streamable_http_transport, get_full_tools_list


class ChatAgent:
    """Strands Agent実装（MCPクライアント版）"""
    
    def __init__(self):
        self.agent = None
        self.model = None
        self.mcp_client = None
        self.tools = []
        self._initialize()
    
    def _initialize(self):
        """エージェントを初期化"""
        try:
            # Geminiモデルの設定
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEYが設定されていません")
            
            self.model = GeminiModel(
                client_args={"api_key": GEMINI_API_KEY},
                model_id="gemini-2.5-flash-lite",
                params={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                    "top_p": 0.9,
                    "top_k": 40
                }
            )
            
            # アクセストークンを取得
            access_token = fetch_access_token(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
            print(f"✅ アクセストークン取得完了")
            
            # MCPクライアントを作成
            self.mcp_client = MCPClient(lambda: create_streamable_http_transport(GATEWAY_URL, access_token))
            
            # MCPクライアントからツール一覧を取得
            with self.mcp_client:
                self.tools = get_full_tools_list(self.mcp_client)
                print(f"✅ 発見されたツール: {len(self.tools)}個")
                for tool in self.tools:
                    tool_name = getattr(tool, 'tool_name', 'Unknown')
                    tool_desc = getattr(tool, 'description', 'No description available')
                    print(f"  - {tool_name}: {tool_desc}")
            
            # Strands Agentの作成
            self.agent = Agent(
                model=self.model,
                system_prompt=SYSTEM_PROMPT,
                tools=self.tools
            )
            
            print("✅ Strands Agent初期化完了")
            tool_names = [getattr(tool, 'tool_name', 'Unknown') for tool in self.tools]
            print(f"🔧 利用可能なツール: {tool_names}")
            
        except Exception as e:
            print(f"❌ Strands Agent初期化エラー: {str(e)}")
            raise
    
    def chat(self, message: str, session_id: str = "default") -> str:
        """チャットメッセージを処理"""
        try:
            if not self.agent:
                return "エラー: エージェントが初期化されていません。"
            
            # MCPクライアントのコンテキスト内でエージェントを実行
            with self.mcp_client:
                result = self.agent(message)
                response_text = str(result)
                return response_text
            
        except Exception as e:
            return f"チャット処理中にエラーが発生しました: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """エージェント状態を取得"""
        return {
            "gateway_url": GATEWAY_URL,
            "client_configured": bool(CLIENT_ID and CLIENT_SECRET),
            "mcp_client_configured": self.mcp_client is not None,
            "available_tools": [getattr(tool, 'tool_name', 'Unknown') for tool in self.tools]
        }
