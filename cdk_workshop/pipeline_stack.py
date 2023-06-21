from constructs import Construct
from aws_cdk import (
    Stack, aws_codecommit as codecommit, pipelines
)

class WorkshopPipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        repo = codecommit.Repository(
            self, "WorkshopRepo",
            repository_name="WorkshopRepo"
        )

        pipeline = pipelines.CodePipeline(
            self, "Pipeline",
            # "synth", describes the commands necessary to build the CDK application from source
            # should always end to a `synth` command
            synth=pipelines.ShellStep( 
            "Synth", 
            input=pipelines.CodePipelineSource.code_commit(repo, "main"), # the repository of the CDK code
            commands=[
                "npm install -g aws-cdk",
                "pip install -r requirements.txt",
                "cdk synth"
            ]
            )
        )