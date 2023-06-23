#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.stacks.pipeline_stack import CodePipelineStack


app = cdk.App()
CodePipelineStack(app, "CodePipelineStack")

app.synth()
