"""
ユーティリティ関数
"""
import requests
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client


def fetch_access_token(client_id: str, client_secret: str, token_url: str) -> str:
    """OAuth2アクセストークンを取得"""
    response = requests.post(
        token_url,
        data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}",
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    return response.json()['access_token']


def create_streamable_http_transport(mcp_url: str, access_token: str):
    """MCP用のHTTPトランスポートを作成"""
    return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {access_token}"})


def get_full_tools_list(client):
    """MCPクライアントからツール一覧を取得（ページネーション対応）"""
    more_tools = True
    tools = []
    pagination_token = None
    
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        
        if tmp_tools.pagination_token is None:
            more_tools = False
        else:
            more_tools = True
            pagination_token = tmp_tools.pagination_token
    
    return tools
