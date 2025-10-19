"""
チャットセッション管理モジュール

このモジュールは、LangChainベストプラクティスに従った
チャットセッションの管理機能を提供します。
エラーハンドリングとフォールバック機能を含みます。
"""

from .context import Context
from .agent import ResponseFormat

class ChatSession:
    """
    LangChainベストプラクティスに従ったチャットセッション管理クラス
    
    このクラスは、ユーザーとエージェント間の会話セッションを管理し、
    エラーハンドリングとフォールバック機能を提供します。
    """
    
    def __init__(self, agent, user_id: str = "1"):
        """
        チャットセッションを初期化
        
        Args:
            agent: LangChainエージェントインスタンス
            user_id (str): ユーザーID（デフォルト: "1"）
        """
        self.agent = agent
        self.user_id = user_id
        # セッション設定（スレッドIDで会話を区別）
        self.config = {"configurable": {"thread_id": f"user_{user_id}"}}
        # コンテキスト管理
        self.context = Context(user_id=user_id)
        
    def send_message(self, message: str) -> ResponseFormat:
        """
        ユーザーメッセージをエージェントに送信し、レスポンスを返す
        
        Args:
            message (str): ユーザーからのメッセージ
            
        Returns:
            ResponseFormat: エージェントからの応答
            
        Note:
            - 再帰制限エラーが発生した場合はフォールバック応答を実行
            - ツール呼び出しエラーなどの適切なエラーハンドリングを提供
        """
        print(f"📤 send_message開始: {message[:50]}...")
        try:
            # 再帰制限を設定してツール呼び出しの無限ループを防止
            config_with_limit = {
                **self.config,
                "recursion_limit": 5
            }
            
            # エージェントを呼び出し
            messages = [{"role": "user", "content": message}]
            response = self.agent.invoke(
                {"messages": messages},
                config=config_with_limit,
                context=self.context
            )
            
            
            # レスポンスの処理
            result = self._process_response(response)
            print(f"✅ send_message成功: {result.response[:50]}...")
            return result
                
        except Exception as e:
            error_msg = str(e)
            print(f"セッションエラー詳細: {error_msg}")
            import traceback
            print(f"スタックトレース: {traceback.format_exc()}")
            
            # 再帰制限エラーの場合はシンプルな応答を返す
            if "Recursion limit" in error_msg or "GraphRecursionError" in str(type(e)):
                print("⚠️ 再帰制限エラーが発生しました。")
                return ResponseFormat(
                    response="申し訳ございませんが、処理が複雑すぎるようです。もう少しシンプルな質問にしていただけますか？"
                )
            
            print(f"❌ send_messageエラー: {error_msg}")
            return ResponseFormat(
                response=f"申し訳ございませんが、エラーが発生しました: {error_msg}"
            )
    
    def _process_response(self, response) -> ResponseFormat:
        """
        エージェントからの応答を処理する共通メソッド
        
        Args:
            response: エージェントからの応答
            
        Returns:
            ResponseFormat: 処理された応答
        """
        if 'structured_response' in response:
            return response['structured_response']
        elif 'messages' in response and response['messages']:
            last_message = response['messages'][-1]
            if hasattr(last_message, 'content'):
                return ResponseFormat(response=last_message.content)
            else:
                return ResponseFormat(response=str(last_message))
        else:
            return ResponseFormat(response="応答を取得できませんでした。")
    