import streamlit as st
import boto3
import json
import uuid
import os
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="Compass Chat UI",
    page_icon="🤖",
    layout="wide"
)

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# AWS Bedrock Agent Core クライアントの初期化
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agentcore', region_name='ap-northeast-1')

# エージェント呼び出し関数
def invoke_agent(prompt):
    """AWS Agent Coreエージェントを呼び出し"""
    try:
        # 環境変数からagentRuntimeArnを取得
        agent_runtime_arn = os.getenv('AGENT_RUNTIME_ARN')
        if not agent_runtime_arn:
            return "エラー: AGENT_RUNTIME_ARN環境変数が設定されていません"
        
        client = get_bedrock_client()
        payload = json.dumps({
            "prompt": prompt
        })
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=st.session_state.session_id,
            payload=payload,
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        # レスポンスからメッセージを抽出
        if 'result' in response_data:
            return response_data['result']
        elif 'completion' in response_data:
            return response_data['completion']
        elif 'message' in response_data:
            return response_data['message']
        else:
            return str(response_data)
            
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# メインUI
st.title("🤖 Compass Chat UI")
st.caption("AWS Agent Coreエージェントとのチャット")

# サイドバー
with st.sidebar:
    st.header("設定")
    st.write(f"セッションID: {st.session_state.session_id[:8]}...")
    
    if st.button("チャット履歴をクリア"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# チャット履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# チャット入力
if prompt := st.chat_input("メッセージを入力してください..."):
    # ユーザーメッセージを履歴に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # エージェントの応答を取得
    with st.chat_message("assistant"):
        with st.spinner("エージェントが応答を生成中..."):
            response = invoke_agent(prompt)
            st.markdown(response)
    
    # エージェントの応答を履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": response})

# フッター
st.markdown("---")
st.caption("Powered by AWS Bedrock Agent Core")
