# index.py
import json
import os
import urllib.request

# FastAPIサーバーのエンドポイント
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://27fb-34-16-249-129.ngrok-free.app/generate")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # Cognitoの認証情報取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディ解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("Processing message:", message)

        # FastAPIに送るデータ
        payload = {
            "prompt": message
        }

        print(f"Calling FastAPI server {FASTAPI_URL} with payload:", json.dumps(payload))

        # FastAPIサーバーにPOSTリクエスト送信
        req = urllib.request.Request(
            FASTAPI_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as res:
            fastapi_response = json.loads(res.read())

        print("FastAPI response:", json.dumps(fastapi_response, default=str))

        # FastAPIのレスポンスから応答文を取得
        assistant_response = fastapi_response['generated_text']

        # Lambdaのレスポンスとして返す
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation_history + [{"role": "assistant", "content": assistant_response}]
            })
        }

    except Exception as error:
        print("Error:", str(error))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
