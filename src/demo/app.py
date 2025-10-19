"""
Streamlitアプリケーション

このモジュールは、MCPツールを統合したチャットアプリケーションの
メインエントリーポイントです。
ユーザーインターフェース、セッション管理、エラーハンドリングを含みます。
"""

import streamlit as st
import os
from chat.agent import create_my_agent
from chat.session import ChatSession
from chat.mcp_tools import MCPToolManager

# ページ設定
# Streamlitアプリケーションの基本設定
st.set_page_config(
    page_title="Sample Application",  # ブラウザタブのタイトル
    page_icon=":tools:",              # ファビコン（ツールアイコン）
    layout="wide"                     # ワイドレイアウト
)

# セッション状態の初期化
# Streamlitのセッション状態を管理し、アプリケーションの状態を保持
if "agent" not in st.session_state:
    st.session_state.agent = None  # LangChainエージェント
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None  # チャットセッション
if "messages" not in st.session_state:
    st.session_state.messages = []  # チャット履歴
if "mcp_manager" not in st.session_state:
    st.session_state.mcp_manager = MCPToolManager()  # MCPツールマネージャー

def initialize_system():
    """
    システムの初期化（エージェント + MCPツール）
    
    Returns:
        bool: 初期化の成功/失敗
        
    Note:
        - 環境変数の確認
        - MCPツールの初期化
        - エージェントの作成
        - チャットセッションの設定
    """
    try:
        # 環境変数のチェック
        required_env_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            st.error(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")
            st.info("env.shファイルを読み込んでください: `source env.sh`")
            return False
        
        # 初期化
        with st.spinner("初期化中..."):
            # 1. MCPツールを初期化
            mcp_success = st.session_state.mcp_manager.initialize()
            
            # 2. エージェントを作成（MCPツール統合済み）
            st.session_state.agent = create_my_agent()
            st.session_state.chat_session = ChatSession(st.session_state.agent)
            
            
            # 3. 結果を表示（統合版）
            if mcp_success:
                mcp_tool_count = len(st.session_state.mcp_manager.get_tool_names())
                st.success(f"✅ 初期化完了！MCPツール {mcp_tool_count}個利用可能")
            else:
                st.success("✅ 初期化完了！基本機能のみ利用可能")
            
            return True
        
    except Exception as e:
        st.error(f"初期化に失敗しました: {str(e)}")
        return False

def main():
    """
    メインのStreamlitアプリケーション
    
    この関数は、アプリケーションのメインUIを構築し、
    ユーザーインタラクションを処理します。
    """
    
    # ヘッダー
    # アプリケーションのタイトルと説明
    st.title("Sample Application")
    st.markdown("様々なMCPツールをつかって、様々な機能を提供するサンプルアプリケーションです。")
    
    # サイドバー
    # アプリケーションの設定とステータス表示
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 初期化ボタン（統合版）
        # システム全体の初期化を実行
        if st.button("🚀 初期化", type="primary"):
            if initialize_system():
                st.rerun()
        
        # チャット履歴クリア
        # 会話履歴をリセット
        if st.button("🗑️ チャット履歴をクリア"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # システムステータス（統合表示）
        # 接続状態とツール可用性を表示
        if st.session_state.agent is not None:
            mcp_info = st.session_state.mcp_manager.get_server_info()
            has_tools = st.session_state.mcp_manager.has_available_tools()
            
            if mcp_info["status"] == "接続済み" and has_tools:
                st.success("✅ MCPツール利用可能")
                
                # MCPツール情報
                st.markdown("### 🔗 MCPツール情報")
                st.markdown(f"**ツール数**: {mcp_info['tools_count']}個")
                
                # 利用可能なツール一覧
                if mcp_info['tools']:
                    st.markdown("### 🛠️ 利用可能なMCPツール")
                    for tool in mcp_info['tools']:
                        with st.expander(f"🔧 {tool['name']}"):
                            st.markdown(f"**説明**: {tool['description']}")
            elif mcp_info["status"] == "接続済み" and not has_tools:
                st.warning("⚠️ システム: 接続済み（MCPツールなし）")
            else:
                st.success("✅ システム: 接続済み（基本機能のみ）")
        else:
            st.warning("⚠️ システム: 未接続")
        
        st.markdown("---")
        
        # メッセージ数の表示
        st.markdown(f"💬 メッセージ数: {len(st.session_state.messages)}")
        
    
    # メインコンテンツエリア（チャット履歴）
    # チャット履歴を表示するコンテナ
    chat_container = st.container()
    
    with chat_container:
        # チャット履歴の表示
        # 保存されたメッセージを時系列で表示
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # 固定された入力エリア（下部）
    # ユーザー入力とアシスタント応答の境界線
    st.markdown("---")
    
    # ユーザー入力処理
    # チャット入力フィールドからのメッセージを処理
    if prompt := st.chat_input("メッセージを入力してください...", key="chat_input"):
        # ユーザーメッセージを履歴に追加
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 初期化されていない場合は初期化
        # システムが初期化されていない場合の自動初期化
        if st.session_state.agent is None:
            if not initialize_system():
                st.error("初期化に失敗しました。")
                return
        
        # アシスタント応答の生成と表示
        with st.chat_message("assistant"):
            with st.spinner("処理中..."):
                try:
                    # エージェントにメッセージを送信して応答を取得
                    response = st.session_state.chat_session.send_message(prompt)
                    
                    # エージェントの応答を表示
                    st.markdown(response.response)
                    
                    # メッセージ履歴に追加
                    # 会話履歴を更新
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response.response,
                    })
                    
                except Exception as e:
                    # エラーハンドリング
                    error_msg = str(e)
                    st.error(f"エラーが発生しました: {error_msg}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"申し訳ございませんが、エラーが発生しました: {error_msg}",
                    })
                             
        # ページを自動でスクロール
        # UIの更新を反映
        st.rerun()

if __name__ == "__main__":
    main()