from aws_cdk import aws_lambda
from constructs import Construct


class NotificationParser(Construct):
    @property
    def handler(self):
        return self._handler

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self._handler = aws_lambda.Function(
            self,
            "NotificationParser",
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            code=aws_lambda.Code.from_asset("lambda"),
            handler="notification_parser.handler",
        )
