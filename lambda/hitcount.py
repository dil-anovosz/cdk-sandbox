import json
import os

import boto3

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ["HITS_TABLE_NAME"])
_lambda = boto3.client("lambda")


def handler(event, context):
    print(f"request: {json.dumps(event)}")
    table.update_item(
        Key={"path": event["path"]},
        UpdateExpression="ADD hits :incr",
        ExpressionAttributeValues={":incr": 1},
    )

    resp = _lambda.invoke(
        FunctionName=os.environ["DOWNSTREAM_FUNCTION_NAME"],  # name of lambda function
        Payload=json.dumps(event),
    )

    body = resp["Payload"].read()
    print(f"downstream response: {body}")
    return json.loads(body)
