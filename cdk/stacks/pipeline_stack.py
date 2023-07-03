from aws_cdk import (
    Stack,
    aws_codestarnotifications,
    aws_events_targets,
    aws_sns,
    aws_sns_subscriptions,
    pipelines,
)
from aws_cdk.aws_lambda_event_sources import SnsEventSource
from constructs import Construct

from cdk.assets.lambdas.pipeline_notification_construct import NotificationParser
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
                    connection_arn="arn:aws:codestar-connections:us-west-2:681724587179:connection/c7af9b71-d900-400b-a9f7-68cceb6c4f72",
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

        pipeline.build_pipeline()

        pipeline_notification_rule = pipeline.pipeline.on_event(
            id="PipelineNotification",
            description="Notify on deploys from code commits",
            event_pattern={
                "detail_type": ["CodePipeline Action Execution State Change"],
                "detail": {
                    "execution-result": {
                        "external-execution-summary": [
                            {"prefix": '{"ProviderType":"GitHub","CommitMessage'}
                        ]
                    }
                },
            },
            rule_name="NotifyOnDeployFromCommit",
        )

        topic = aws_sns.Topic(self, "Topic", display_name="Test subscription topic")
        pipeline_notification_rule.add_target(
            aws_events_targets.SnsTopic(
                topic,
            )
        )

        topic.add_subscription(
            aws_sns_subscriptions.EmailSubscription("anovoszath@diligent.com")
        )
        topic.add_subscription(
            aws_sns_subscriptions.EmailSubscription(
                "pipeline-test-notific-aaaakaddfvgdfiomr5sejtgaka@diligent.slack.com"
            )
        )
        notification_parser = NotificationParser(self, "PipelineNotificationParser")        
        notification_parser.handler.add_event_source(SnsEventSource(topic))

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
