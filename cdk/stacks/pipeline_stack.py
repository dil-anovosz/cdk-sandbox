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

        # SNS topic
        topic = aws_sns.Topic(self, "Topic", display_name="Test subscription topic")
        topic.add_subscription(
            aws_sns_subscriptions.EmailSubscription("anovoszath@diligent.com")
        )
        topic.add_subscription(
            aws_sns_subscriptions.EmailSubscription(
                "pipeline-test-notific-aaaakaddfvgdfiomr5sejtgaka@diligent.slack.com"
            )
        )

        # Lambda function
        notification_parser = NotificationParser(self, "PipelineNotificationParser")
        notification_parser.handler.add_event_source(SnsEventSource(topic))

        # Tests, test, test, test, test, test, test, test, test, test, test, test, test, test, test
        # Notification rule
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
        pipeline_notification_rule.add_target(
            aws_events_targets.SnsTopic(
                topic,
                # message=aws_events.RuleTargetInput.from_object(
                #     {
                #         "ExecutionResult": aws_events.EventField.from_path(
                #             "$.detail.execution-result"
                #         )
                #     }
                # ),
            )
        )

        notifier = aws_codestarnotifications.NotificationRule(
            self,
            "PipelineNotification",
            events=[
                "codepipeline-pipeline-action-execution-canceled",
                "codepipeline-pipeline-action-execution-failed",
                "codepipeline-pipeline-action-execution-started",
                "codepipeline-pipeline-action-execution-succeeded",
                # "codepipeline-pipeline-manual-approval-failed",
                # "codepipeline-pipeline-manual-approval-needed",
                # "codepipeline-pipeline-manual-approval-succeeded",
                # "codepipeline-pipeline-pipeline-execution-canceled",
                # "codepipeline-pipeline-pipeline-execution-failed",
                # "codepipeline-pipeline-pipeline-execution-resumed",
                # "codepipeline-pipeline-pipeline-execution-started",
                # "codepipeline-pipeline-pipeline-execution-succeeded",
                # "codepipeline-pipeline-pipeline-execution-superseded",
                # "codepipeline-pipeline-stage-execution-canceled",
                # "codepipeline-pipeline-stage-execution-failed",
                # "codepipeline-pipeline-stage-execution-resumed",
                # "codepipeline-pipeline-stage-execution-started",
                # "codepipeline-pipeline-stage-execution-succeeded",
            ],
            source=pipeline.pipeline,
            enabled=True,
        )
        notifier.add_target(topic)

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
