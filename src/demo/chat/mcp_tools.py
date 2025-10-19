"""
MCPツール管理モジュール

このモジュールは、MCP（Model Context Protocol）ツールの管理と
LangChainツールへの統合機能を提供します。
OAuth2認証、ツール呼び出し、エラーハンドリングを含みます。
"""

import asyncio
import os
import requests
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

def fetch_access_token(client_id: str, client_secret: str, token_url: str) -> str:
    """
    OAuth2クライアントクレデンシャルフローでアクセストークンを取得
    
    Args:
        client_id (str): OAuth2クライアントID
        client_secret (str): OAuth2クライアントシークレット
        token_url (str): トークン取得エンドポイントURL
        
    Returns:
        str: アクセストークン
        
    Raises:
        Exception: トークン取得に失敗した場合
    """
    try:
        print(f"OAuth2トークン取得中: {token_url}")
        response = requests.post(
            token_url,
            data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"トークン取得失敗: HTTP {response.status_code} - {response.text}")
        
        token_data = response.json()
        if 'access_token' not in token_data:
            raise Exception(f"トークンレスポンスにaccess_tokenが含まれていません: {token_data}")
        
        print("OAuth2トークン取得成功")
        return token_data['access_token']
        
    except Exception as e:
        print(f"OAuth2トークン取得エラー: {str(e)}")
        raise

class MCPToolWrapper(BaseTool):
    """
    MCPツールをLangChainツールとしてラップするクラス
    
    このクラスは、MCPプロトコルで提供されるツールを
    LangChainのBaseToolインターフェースに適合させます。
    同期・非同期両方の実行をサポートします。
    """
    
    # 必須フィールドをOptionalに変更
    # LangChainのBaseToolとの互換性のため
    mcp_tool_name: Optional[str] = None
    gateway_url: Optional[str] = None
    access_token: Optional[str] = None
    
    def __init__(self, mcp_tool_name: str, description: str, gateway_url: str, access_token: str):
        """
        MCPツールラッパーを初期化
        
        Args:
            mcp_tool_name (str): MCPツールの名前
            description (str): ツールの説明
            gateway_url (str): MCPゲートウェイのURL
            access_token (str): 認証用アクセストークン
        """
        # 親クラスの初期化を適切に行う
        super().__init__(
            name=mcp_tool_name,
            description=description
        )
        # インスタンス変数として設定
        self.mcp_tool_name = mcp_tool_name
        self.gateway_url = gateway_url
        self.access_token = access_token

    
    def _run(self, **kwargs) -> str:
        """
        MCPツールを実行（同期版）
        
        LangChainの同期インターフェースに合わせて、
        非同期のMCPツール呼び出しを同期処理で実行します。
        
        Args:
            **kwargs: ツールに渡すパラメータ
            
        Returns:
            str: ツール実行結果またはエラーメッセージ
        """
        try:
            # run_agent.pyの方式に合わせて同期処理
            # 新しいイベントループを作成して非同期処理を実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self._arun(**kwargs))
                return result
            finally:
                loop.close()
        except Exception as e:
            # エラーが発生した場合の処理
            error_msg = f"MCPツール '{self.mcp_tool_name}' の実行中にエラーが発生しました: {str(e)}"
            print(error_msg)
            return error_msg
    
    async def _arun(self, **kwargs) -> str:
        """
        MCPツールを実行（非同期版）
        
        MCPプロトコルを使用してツールを非同期で実行します。
        パラメータ検証、認証、エラーハンドリングを含みます。
        
        Args:
            **kwargs: ツールに渡すパラメータ
            
        Returns:
            str: ツール実行結果またはエラーメッセージ
        """
        # 設定の検証
        if not self.gateway_url or not self.access_token:
            return "MCPツールの設定が不完全です"
        
        # パラメータ検証を追加
        # 特定のツールで必須パラメータをチェック
        if self.mcp_tool_name == "x_amz_bedrock_agentcore_search":
            if not kwargs.get("query"):
                return "検索ツールには必須の'query'パラメータが必要です。検索クエリを指定してください。"
        
        try:
            # 認証ヘッダーの設定
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            # デバッグ情報の出力
            print(f"🔧 MCPツール呼び出し開始: {self.mcp_tool_name}")
            print(f"📝 引数: {kwargs}")
            print(f"🌐 ゲートウェイURL: {self.gateway_url}")
            print(f"🔑 アクセストークン: {'設定済み' if self.access_token else '未設定'}")
            
            # MCPクライアントを使用してツールを実行
            async with streamablehttp_client(
                url=self.gateway_url,
                headers=headers,
            ) as (read_stream, write_stream, callA):
                async with ClientSession(read_stream, write_stream) as session:
                    # セッションの初期化
                    print(f"🔄 セッション初期化中: {self.mcp_tool_name}")
                    await session.initialize()
                    print(f"✅ セッション初期化完了: {self.mcp_tool_name}")
                    
                    # ツールの実行
                    print(f"🚀 ツール実行中: {self.mcp_tool_name}")
                    result = await session.call_tool(
                        name=self.mcp_tool_name,
                        arguments=kwargs
                    )
                    
                    print(f"✅ ツール呼び出し成功: {self.mcp_tool_name}")
                    
                    # 結果の処理を改善
                    # 複数の結果形式に対応
                    if hasattr(result, 'content') and result.content:
                        return str(result.content)
                    elif hasattr(result, 'text') and result.text:
                        return str(result.text)
                    else:
                        return f"ツール '{self.mcp_tool_name}' の実行が完了しましたが、結果が空です。"
                    
        except Exception as e:
            # エラーハンドリング
            error_msg = str(e)
            print(f"MCPツール '{self.mcp_tool_name}' エラー詳細: {error_msg}")
            import traceback
            print(f"詳細なエラー情報: {traceback.format_exc()}")
            
            # エラーメッセージの返却
            return f"ツール '{self.mcp_tool_name}' の実行中にエラーが発生しました: {error_msg}"

class MCPToolManager:
    """
    MCPツールを管理し、LangChainツールとして提供するクラス
    
    このクラスは、MCPゲートウェイとの接続、ツール一覧の取得、
    LangChainツールへの変換を管理します。
    """
    
    def __init__(self):
        """
        MCPツールマネージャーを初期化
        
        Attributes:
            gateway_url (str): MCPゲートウェイのURL
            access_token (str): 認証用アクセストークン
            tools (list): 利用可能なツール一覧
            initialized (bool): 初期化完了フラグ
        """
        self.gateway_url = None
        self.access_token = None
        self.tools = []
        self.initialized = False
    
    def initialize(self) -> bool:
        """MCPゲートウェイに接続してツール一覧を取得"""
        try:
            # 環境変数から設定を取得
            required_env_vars = [
                "MCP_GATEWAY_URL",
                "MCP_CLIENT_ID",
                "MCP_CLIENT_SECRET",
                "MCP_TOKEN_URL"
            ]
            
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            if missing_vars:
                print(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")
                return False
            
            print("MCPゲートウェイに接続中...")
            
            # アクセストークンを取得
            client_id = os.getenv("MCP_CLIENT_ID")
            client_secret = os.getenv("MCP_CLIENT_SECRET")
            token_url = os.getenv("MCP_TOKEN_URL")
            
            print(f"トークン取得中: {token_url}")
            self.access_token = fetch_access_token(client_id, client_secret, token_url)
            self.gateway_url = os.getenv("MCP_GATEWAY_URL")
            print(f"アクセストークン取得完了: {self.gateway_url}")
            
            # ツール一覧を取得
            print("ツール一覧を取得中...")
            self.tools = asyncio.run(self._get_tools_list())
            self.initialized = True
            
            print(f"MCPゲートウェイに接続しました。利用可能なツール: {len(self.tools)}個")
            for tool in self.tools:
                print(f"  - {tool.name}: {tool.description}")
            return True
            
        except Exception as e:
            print(f"MCP接続エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _get_tools_list(self) -> List[Dict[str, Any]]:
        """利用可能なツール一覧を取得"""
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with streamablehttp_client(
                url=self.gateway_url,
                headers=headers,
            ) as (read_stream, write_stream, callA):
                async with ClientSession(read_stream, write_stream) as session:
                    # 初期化
                    print("MCPセッション初期化中...")
                    await session.initialize()
                    print("MCPセッション初期化完了")
                    
                    # 利用可能なツールをリスト
                    cursor = True
                    tools = []
                    while cursor:
                        next_cursor = cursor
                        if type(cursor) == bool:
                            next_cursor = None
                        print(f"ツール一覧取得中... (cursor: {cursor})")
                        list_tools_response = await session.list_tools(next_cursor)
                        tools.extend(list_tools_response.tools)
                        cursor = list_tools_response.nextCursor
                        print(f"取得したツール数: {len(list_tools_response.tools)}")
                    
                    print(f"全ツール取得完了: {len(tools)}個")
                    return tools
        except Exception as e:
            print(f"ツール一覧取得エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_langchain_tools(self) -> List[BaseTool]:
        """LangChainツールとして利用可能なツール一覧を取得"""
        if not self.initialized:
            print("MCPツールが初期化されていません")
            return []
        
        if not self.tools or len(self.tools) == 0:
            print("利用可能なMCPツールがありません")
            return []
        
        print(f"MCPツールをLangChainツールに変換中... ({len(self.tools)}個)")
        langchain_tools = []
        for tool in self.tools:
            try:
                # MCPツールをLangChainツールとしてラップ
                wrapped_tool = MCPToolWrapper(
                    mcp_tool_name=tool.name,
                    description=tool.description or f"MCP tool: {tool.name}",
                    gateway_url=self.gateway_url,
                    access_token=self.access_token
                )
                langchain_tools.append(wrapped_tool)
                print(f"  ✅ {tool.name}: 変換成功")
            except Exception as e:
                print(f"  ❌ ツール '{tool.name}' のラップに失敗: {str(e)}")
                continue
        
        print(f"LangChainツール変換完了: {len(langchain_tools)}個")
        return langchain_tools
    
    def get_tool_names(self) -> List[str]:
        """利用可能なツール名一覧を取得"""
        if not self.initialized:
            return []
        return [tool.name for tool in self.tools]
    
    def has_available_tools(self) -> bool:
        """利用可能なツールがあるかどうかを判定"""
        return self.initialized and self.tools and len(self.tools) > 0
    
    def get_available_tools(self) -> List[BaseTool]:
        """利用可能なツールのみを返す（動的取得）"""
        if self.has_available_tools():
            return self.get_langchain_tools()
        else:
            return []

    def get_server_info(self) -> Dict[str, Any]:
        """MCPサーバの情報を取得"""
        if not self.initialized:
            return {
                "status": "未接続",
                "tools_count": 0,
                "tools": [],
                "gateway_url": "未設定"
            }
        
        return {
            "status": "接続済み",
            "tools_count": len(self.tools),
            "tools": [{"name": tool.name, "description": tool.description} for tool in self.tools],
            "gateway_url": self.gateway_url
        }        