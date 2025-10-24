import requests
import json

import os
CLIENT_ID = os.environ.get("MCP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("MCP_CLIENT_SECRET")
TOKEN_URL = os.environ.get("MCP_TOKEN_URL")

def fetch_access_token(client_id, client_secret, token_url):
  if not token_url:
    raise ValueError("MCP_TOKEN_URL が設定されていません")
  if not client_id:
    raise ValueError("MCP_CLIENT_ID が設定されていません")
  if not client_secret:
    raise ValueError("MCP_CLIENT_SECRET が設定されていません")
  
  response = requests.post(
    token_url,
    data="grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}".format(client_id=client_id, client_secret=client_secret),
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
  )
  if response.status_code != 200:
    raise RuntimeError("トークン取得に失敗しました: {status} {text}".format(status=response.status_code, text=response.text))
  
  body = response.json()
  if 'access_token' not in body:
    raise RuntimeError("レスポンスに access_token が含まれていません: {body}".format(body=body))
  return body['access_token']

def call_openapi_tool(gateway_url, access_token, tool_name, arguments):
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {access_token}"
  }

  payload = {
      "jsonrpc": "2.0",
      "id": "openapi-call-1",
      "method": "tools/call",
      "params": {
          "name": tool_name,
          "arguments": arguments
      }
  }

  response = requests.post(gateway_url, headers=headers, json=payload)
  return response.json()

def list_tools_names(gateway_url, access_token):
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {access_token}"
  }
  payload = {
      "jsonrpc": "2.0",
      "id": "list-tools-request",
      "method": "tools/list"
  }
  response = requests.post(gateway_url, headers=headers, json=payload)
  data = response.json()
  tools = data.get('result', {}).get('tools', [])
  names = []
  for t in tools:
    name = t.get('name') if isinstance(t, dict) else None
    if name:
      names.append(name)
  return names
 
def main():
  gateway_url = os.environ.get("GATEWAY_URL", "https://testgatewaya7b892fc-2ctubxxyys.gateway.bedrock-agentcore.ap-northeast-1.amazonaws.com/mcp")
  
  try:
    access_token = fetch_access_token(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
  except Exception as e:
    print("環境変数またはトークン取得でエラーが発生しました: {e}".format(e=e))
    return
  
  # まずツール名の一覧を表示
  try:
    names = list_tools_names(gateway_url, access_token)
    print("=== 利用可能なツール名 ===")
    for n in names:
      print(f"- {n}")
  except Exception as e:
    print("ツール一覧の取得に失敗しました: {e}")
  
  
  # === OpenAPIツール（Gatewayに登録済み）を直接呼び出す ===
  openapi_tool_name = os.environ.get("OPENAPI_TOOL_NAME", "azure-gpt-4o-mini___createChatCompletion")
  print("\n=== OpenAPIツールをtools/callで呼び出し ===")
  api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
  openapi_arguments = {
    "api-version": api_version,
    "messages": [
      {"role": "user", "content": "こんにちは！今日の天気はどうですか？"}
    ],
    "temperature": 0.7,
    "max_tokens": 200
  }
  openapi_resp = call_openapi_tool(
    gateway_url=gateway_url,
    access_token=access_token,
    tool_name=openapi_tool_name,
    arguments=openapi_arguments,
  )
  print(json.dumps(openapi_resp, indent=2, ensure_ascii=False))

if __name__ == "__main__":
  main()