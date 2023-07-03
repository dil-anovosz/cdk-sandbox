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
    webhook_token = json.loads(get_secret_value_response["SecretString"])["token"]

    eventbridge = event["Records"][0]["Sns"]["Message"]["detail"]
    commit_text = json.loads(
        eventbridge["execution-result"]["external-execution-summary"]
    )["CommitMessage"]
    pr_info, commit_message = commit_text.split("\n\n")

    msg = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":hammer_and_wrench: *{eventbridge['state']} | {eventbridge['region']}*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Pipeline*: {eventbridge['pipeline']}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{eventbridge['execution-result']['external-execution-url']}|{pr_info}>",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Message:*\n{commit_message}",
                },
            },
            {"type": "divider"},
        ],
    }

    encoded_msg = json.dumps(msg).encode("utf-8")
    resp = http.request("POST", webhook_token, body=encoded_msg)

    return json.loads(encoded_msg)
