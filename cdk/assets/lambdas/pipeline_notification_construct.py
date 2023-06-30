from aws_cdk import aws_lambda
from aws_cdk import aws_iam
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

        self._handler.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue",
                ],
                resources=[
                    "arn:aws:lambda:us-west-2:681724587179:function:CodePipelineStack-PipelineNotificationParser891594-TA3zz3bbVkZW:*",
                ],
            )
        )
