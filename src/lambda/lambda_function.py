import json
import os

try:
    # 依存はデプロイ時に同梱してください（google-cloud-bigquery）
    from google.cloud import bigquery
    from google.oauth2 import service_account
except Exception:
    bigquery = None
    service_account = None

def _create_bq_client(project_id: str):
    """
    BigQueryクライアントを作成する。
    環境変数`GCP_SERVICE_ACCOUNT_JSON`があればそれを使用、なければデフォルト認証情報。
    """
    # base64ではなくプレーンJSON文字列を想定（必要なら外側でbase64デコードして格納）
    sa_json = os.getenv('GCP_SERVICE_ACCOUNT_JSON')
    if service_account and sa_json:
        try:
            info = json.loads(sa_json)
            creds = service_account.Credentials.from_service_account_info(info)
            return bigquery.Client(project=project_id, credentials=creds)
        except Exception:
            # 万一壊れたJSONでも、デフォルト認証にフォールバック
            pass
    # フォールバック: ランタイムのデフォルト認証
    return bigquery.Client(project=project_id) if bigquery else None

def _list_bigquery_tables(project_id: str, dataset_id: str | None = None):
    """指定データセットのテーブルID一覧を返す。"""
    client = _create_bq_client(project_id)
    if client is None:
        raise RuntimeError('BigQueryクライアントが利用できません。依存関係(google-cloud-bigquery)を同梱してください。')

    dataset_ref = f"{project_id}.{dataset_id}"
    tables_iter = client.list_tables(dataset_ref, max_results=None)
    table_ids = [t.table_id for t in tables_iter]
    return table_ids

def lambda_handler(event, context):
    # tool_nameを安全に取得（context → event の順でフォールバック）
    tool_name = 'unknown'
    try:
        client_context = getattr(context, 'client_context', None)
        custom = getattr(client_context, 'custom', None)
        if isinstance(custom, dict):
            tool_name = custom.get('bedrockAgentCoreToolName', tool_name)
    except Exception:
        pass
    if isinstance(event, dict):
        tool_name = event.get('tool_name', tool_name) or tool_name

    if 'get_bigquery' in tool_name:
        # 入力はeventから受け取る。無ければ環境変数のデフォルトを使用。
        project_id = event.get('project_id') or os.getenv('BQ_DEFAULT_PROJECT_ID')
        dataset_id = event.get('dataset_id') or os.getenv('BQ_DEFAULT_DATASET_ID')

        # いずれも未設定の場合のみエラー（環境変数があれば必須ではない）
        if not project_id or not dataset_id:
            missing = []
            if not project_id:
                missing.append('project_id')
            if not dataset_id:
                missing.append('dataset_id')
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f"{', '.join(missing)} を指定するか、環境変数(BQ_DEFAULT_PROJECT_ID/BQ_DEFAULT_DATASET_ID)を設定してください"})
            }

        try:
            tables = _list_bigquery_tables(project_id=project_id, dataset_id=dataset_id)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'project_id': project_id,
                    'dataset_id': dataset_id,
                    'tables': tables
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    elif 'get_googledrive' in tool_name:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'これはGoogle DriveのMCPツールです.Google Driveには100万件のドキュメントが入っています。'
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Unknown tool'})
        }