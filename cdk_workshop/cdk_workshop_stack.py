from constructs import Construct
from aws_cdk import (
    # Duration,
    Stack,
    CfnOutput,
    # aws_iam as iam,
    # aws_sqs as sqs,
    # aws_sns as sns,
    # aws_sns_subscriptions as subs,
    aws_lambda as _lambda,  # '_' naming to avoid collision with builtin `lambda` name
    aws_apigateway as apigw,
)

from cdk_dynamo_table_view import TableViewer
from .hitcounter import HitCounter


class CdkWorkshopStack(Stack):
    @property
    def hc_endpoint(self):
        return self._hc_endpoint

    @property
    def hc_viewer_url(self):
        return self._hc_viewer_url

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # AWS Lambda resource
        my_lambda = _lambda.Function(
            self,
            "HelloHandler",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset("lambda"),  # 'lambda' directory
            handler="hello.handler",  # 'hello' module, 'handler' function
        )

        hello_with_counter = HitCounter(self, "HelloHitCounter", downstream=my_lambda)

        gateway = apigw.LambdaRestApi(
            self, "Endpoint", handler=hello_with_counter.handler
        )

        tv = TableViewer(
            self,
            "ViewHitCounter",
            title="Hello Hits",
            table=hello_with_counter.table,
            sort_by="-hits",
        )

        self._hc_endpoint = CfnOutput(self, "GatewayUrl", value=gateway.url)

        self._hc_viewer_url = CfnOutput(self, "TableViewerUrl", value=tv.endpoint)
