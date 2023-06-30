import json
from urllib3 import PoolManager

import boto3

http = PoolManager()
session = boto3.session.Session()
secretsmanager = session.client(service_name="secretsmanager", region_name="us-west-2")


def handler(event, context):
    print(f"request: {json.dumps(event)}")

    get_secret_value_response = secretsmanager.get_secret_value(
        SecretId="arn:aws:secretsmanager:us-west-2:681724587179:secret:TestSlackWebhookToken-BRXYiK"
    )
    webhook_token = get_secret_value_response["SecretString"]

    msg = {
        "channel": "#pipeline-notification-test",
        "username": "Pipeline Deploy Watcher Bot",
        "text": event["Records"][0]["Sns"]["Message"],
        "icon_emoji": ":space_invader:",
    }

    encoded_msg = json.dumps(msg).encode("utf-8")
    resp = http.request("POST", webhook_token, body=encoded_msg)
    print(
        "After encoding:\n",
        {
            "message": encoded_msg,
            "status_code": resp.status,
            "response": resp.data,
        },
    )

    return json.loads(encoded_msg)
