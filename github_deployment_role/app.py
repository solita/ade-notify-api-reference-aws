#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.deployment_roles_stack import DeploymentRolesStack

app = cdk.App()

deployment_role_stack = DeploymentRolesStack(
    app, 
    f"{app.node.try_get_context('project')}-stack",
    github_org       = app.node.try_get_context('github_org'),
    github_repo_name = app.node.try_get_context('github_repo_name'),
    github_branch    = app.node.try_get_context('github_branch'),
    deploy_env       = app.node.try_get_context('deploy_env'),
    aws_github_provider_arn = app.node.try_get_context('aws_github_provider_arn')
)

app.synth()