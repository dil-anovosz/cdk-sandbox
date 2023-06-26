from constructs import Construct
from aws_cdk import Stack, pipelines, aws_sns, aws_sns_subscriptions, aws_codestarnotifications
from cdk.stages.pipeline_stage import CodePipelineStage


class CodePipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    "dil-anovosz/cdk-sandbox",
                    "main",
                    connection_arn="arn:aws:codestar-connections:us-east-1:681724587179:connection/e148970f-1012-4d76-9df2-3448b9d03e87",
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "pip install -r requirements.txt",
                    "cdk synth",
                ],
            ),
        )

        deploy = CodePipelineStage(self, "Deploy")
        deploy_stage = pipeline.add_stage(deploy)

        # SNS notification
        topic = aws_sns.Topic(
            self, "Topic", display_name="Test subscription topic"
        )
        topic.add_subscription(aws_sns_subscriptions.EmailSubscription("anovoszath@diligent.com"))

        # Notification rule
        notification = aws_codestarnotifications.NotificationRule(
            self,
            "PipelineNotification",
            targets=[topic]
        )

        # Tests
        deploy_stage.add_post(
            pipelines.ShellStep(
                "TestViewerEndpoint",
                env_from_cfn_outputs={"ENDPOINT_URL": deploy.hc_viewer_url},
                commands=["curl -Ssf $ENDPOINT_URL"],
            )
        )
        deploy_stage.add_post(
            pipelines.ShellStep(
                "TestAPIGateWayEndpoint",
                env_from_cfn_outputs={"ENDPOINT_URL": deploy.hc_endpoint},
                commands=[
                    "curl -Ssf $ENDPOINT_URL",
                    "curl -Ssf $ENDPOINT_URL/hello",
                    "curl -Ssf $ENDPOINT_URL/hello/world",
                ],
            )
        )
