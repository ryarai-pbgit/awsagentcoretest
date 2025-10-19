# Agent Core検証用
MCPやA2Aの基盤として有力なサービス、2025/10にGAされたAgent Coreを検証するリポジトリ。<br>
初歩的なところから多数の試行錯誤が発生するため、独立。

## 1. 初めてのAgent Core（2025/10/19）
 https://docs.aws.amazon.com/ja_jp/bedrock-agentcore/latest/devguide/agentcore-get-started-toolkit.html<br>
 上記の通りに進めました、ドキュメントの内容からこちらで変更した点、注目した結果などを中心に記載。<br>

- エージェントのソースコード
[src/agentcore_starter_strands.py](src/agentcore_starter_strands.py)
モデルIDを公式に記載の"us.anthropic.claude-3-7-sonnet-20250219-v1:0"だとエラーになっため、エラーにならないモデルにしました。<br>
```python
# Claude以外のモデルに変更。
MODEL_ID = "apac.amazon.nova-lite-v1:0"
```

- ローカルの準備
AWS CLIのセットアップ（別件でTerraform使うので実施済み）、Agentをローンチするときにコンテナ化するようで、Docker Desktopを起動。

- 短期、長期メモリは下記のような感じになりました。
```
# 短期メモリ
イベント 2: gen_ai.user.message
    "text": "Remember that my favorite agent platform is AgentCore"
（短期メモリされる）
イベント 4: gen_ai.user.message
    "text": "What is my favorite agent platform?"
イベント 5: gen_ai.assistant.message
    The user's favorite agent platform is AgentCore.

# 長期メモリ回答だけ
<thinking>
  The User has provided context regarding their favorite agent platform being AgentCore. 
  To give a more comprehensive response, I might need additional details such as:
  - What specific features they like about AgentCore
  - Their experience with other platforms
  - How they use AgentCore
  
  However, I can provide some general information about AgentCore based on my pre-existing knowledge.
</thinking>

<response>
  AgentCore is a highly adaptable and user-friendly platform for interacting with various types of agents. 
  It is known for its intuitive interface and robust functionality, making it a favorite among users who value efficiency and ease of use. 
  
  If you have specific features or experiences you'd like to discuss about AgentCore, feel free to share more details!
</response>

# 先ほど教えた自分のEmailアドレスを教えて、と聞くと
<thinking>
  The User has not provided any information regarding their email or preferences about it. 
  I can't provide details about the User's email as it's a personal information and it's not available in the provided context. 
  I should ask the User for more information about their email if they want to share it.
</thinking>

<response>
  I'm sorry, but I can't provide details about your email as it's a personal information. 
  If you want to share more information about your email, please let me know!
</response>
```
セッションID変えても、Agent Coreがfavoriteという情報が残っているから良いのかな、と思いました。

## 2. 初めてのAgent Core Gateway（2025/10/19）
https://docs.aws.amazon.com/ja_jp/bedrock-agentcore/latest/devguide/gateway-quick-start.html<br>
上記を実施することで、Gatewayの関連リソースが一式できるようなので、動かして内容を確認していきます。<br>
公式ドキュメントの内容から少し変更しています。（Bedrock初回のClaudeの許諾に会社名とか必要なのでやめました）<br>
モデルIDと推論プロファイルIDの違いがわかっておらず、キャッシュか？とかいうので数時間悶絶しました。<br>
（model_idで与えているものとは違うモデルが実行時に設定されるように見えていました。）

### 2.1 まずはチュートリアルが動作するまで
```python

# setup_gateway.py
def setup_gateway():
    # Configuration
    region = "ap-northeast-1"  # Change to your preferred region

# run_agent.py

    # Model configuration - change if needed
    # Using a more widely available model
    model_id = "apac.amazon.nova-lite-v1:0"

    # Setup Bedrock model
    bedrockmodel = BedrockModel(
#        inference_profile_id=model_id,
        model_id=model_id,
        streaming=True,
    )

```
エージェント動作の様子は下記のような感じです。<br>
質問に合わせてMCPツールを選んで利用していることがわかります。<br>
MCPをモックにして固定情報を与えているので、それが応答されていれば機能しているということだと思います。<br>
```bash
agentcore-gateway-quickstart % python run_agent.py
Getting access token...
2025-10-19 15:16:21,441 - bedrock_agentcore.gateway - INFO - Fetching test token from Cognito...
2025-10-19 15:16:21,442 - bedrock_agentcore.gateway - INFO -   Attempting to connect to token endpoint: https://agentcore-280ce7a2.auth.ap-northeast-1.amazoncognito.com/oauth2/token
2025-10-19 15:16:22,226 - bedrock_agentcore.gateway - INFO - ✓ Got test token successfully
✓ Access token obtained

🤖 Starting AgentCore Gateway Test Agent
Gateway URL: https://testgatewaya7b892fc-2ctubxxyys.gateway.bedrock-agentcore.ap-northeast-1.amazonaws.com/mcp
Model: apac.amazon.nova-lite-v1:0
------------------------------------------------------------

📋 Available tools: ['x_amz_bedrock_agentcore_search', 'TestGatewayTarget94053631___get_time', 'TestGatewayTarget94053631___get_weather']
------------------------------------------------------------

💬 Interactive Agent Ready!
Try asking: 'What's the weather in Seattle?'
Type 'exit', 'quit', or 'bye' to end.

You: 東京の気温は何度ですか度Cで教えて、あと今何時ですか？JSTで答えて。

🤔 Thinking...

<thinking>The User wants to know the current temperature and time in Tokyo. I need to use the `TestGatewayTarget94053631___get_weather` tool to get the temperature and the `TestGatewayTarget94053631___get_time` tool to get the current time in JST (Japan Standard Time). I will call these tools to get the required information.</thinking>

Tool #1: TestGatewayTarget94053631___get_weather

Tool #2: TestGatewayTarget94053631___get_time
<thinking>I have successfully retrieved the weather and time information for Tokyo. The temperature is given in Fahrenheit, so I need to convert it to Celsius using the formula (°F - 32) * 5/9. I will then provide the temperature in Celsius and the current time in JST.</thinking>

The current temperature in Tokyo is approximately 22°C, and the current time is 2:30 PM JST. The weather is sunny.
Agent: [{'text': '<thinking>I have successfully retrieved the weather and time information for Tokyo. The temperature is given in Fahrenheit, so I need to convert it to Celsius using the formula (°F - 32) * 5/9. I will then provide the temperature in Celsius and the current time in JST.</thinking>\n\nThe current temperature in Tokyo is approximately 22°C, and the current time is 2:30 PM JST. The weather is sunny.'}]

You: 日本語で回答して

🤔 Thinking...

<thinking>The User wants the response in Japanese. I will provide the translated information, which includes the current temperature in Celsius and the current time in JST for Tokyo.</thinking>

東京の現在の気温は約22°Cで、現在の時間はJSTで午後2時30分です。天気は晴れています。
Agent: [{'text': '<thinking>The User wants the response in Japanese. I will provide the translated information, which includes the current temperature in Celsius and the current time in JST for Tokyo.</thinking>\n\n東京の現在の気温は約22°Cで、現在の時間はJSTで午後2時30分です。天気は晴れています。'}]

```
### 2.2 生成物を確認する
- Agent Core Gateway
MCPゲートウェイができています。URLやOAuth認証サーバであるCognito、MCPツールを提供するLambdaなどが設定されています。（ARNなど出まくりなので左隅だけ）<br>
![Agent Core Gateway](images/gateway.png)

- Cognito User Pool
こちらも画面は少しだけにしますが、Agent Core Gatewayと紐づく形で生成されています。
![Cognito User Pool](images/cognito_usepool.png)

- Lambda
MCPツールのモックが生成されています。
```python
import json

def lambda_handler(event, context):
    # Extract tool name from context
    tool_name = context.client_context.custom.get('bedrockAgentCoreToolName', 'unknown')

    if 'get_weather' in tool_name:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'location': event.get('location', 'Unknown'),
                'temperature': '72°F',
                'conditions': 'Sunny'
            })
        }
    elif 'get_time' in tool_name:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'timezone': event.get('timezone', 'UTC'),
                'time': '2:30 PM'
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Unknown tool'})
        }

```

## 3. Gatewayを利用するStremlitアプリ：ローカルで試作（2025/10/19）
https://github.com/ryarai-pbgit/genaiplatform<br>
最終的にはこちらとも合流したいところですが、まずはローカルで試作。<br>
ソースコードは[こちら](src/demo)から参照できます。  <br>

- Agent Core Gateway：mcpゲートウェイ
- Cognito：OAuth認証サーバ
- Lambda：mcpツールのモック
- エージェントフレームワーク：LangChain
- UI：Streamlit
- LLM：Azure AI Foundry（もうOpenAIとは言わない。。）でgpt-40-mini

Cursorに色々情報見せながら作ってもらいました。LangChainのtoolにラップしないといけないのか、とかその辺りは理解できたおらず言いなりです。<br>
Cognitoへの認証取得、Gatewayやその先のLambdaへの疎通は確認できました。
ただ、ほっとくとロジックでToolを使う使わないを判定しようとしたので、LLMに判定させて欲しい旨だけ伝えました。<br>
プロンプトの制御もあってか、ユーザ側が明示的にToolを使うように言わないと使わないような感じになっています。<br>

普段の会話しつつ
![サンプルアプリ](images/sampleapp.png)  
ツール使わないわからない中の情報を取得してもらいました
![izanai](images/izanai.png)  

ベースラインができたので、次の方向性としては、、
- mcpツールの実装、Lambdaで良いので実際にBigqueryとGoogleDriveに接続したい
- アプリのサーバ化
- LiteLLM/Langfuseとの統合
の予定。



