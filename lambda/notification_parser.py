import json
from urllib3 import PoolManager

http = PoolManager()


def handler(event, context):
    print(f"request: {json.dumps(event)}")
    url = "https://hooks.slack.com/services/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"
    msg = {
        "channel": "#pipeline-notification-test",
        "username": "Pipeline Deploy Watcher Bot",
        "text": event["Records"][0]["Sns"]["Message"],
        "icon_emoji": ":space_invader:",
    }

    encoded_msg = json.dumps(msg).encode("utf-8")
    resp = http.request("POST", url, body=encoded_msg)
    print(
        "After encoding:\n",
        {
            "message": encoded_msg,
            "status_code": resp.status,
            "response": resp.data,
        },
    )

    return json.loads(encoded_msg)
