import aws_cdk as cdk

from aws_cdk import aws_iam as iam
from constructs import Construct

class DeploymentRolesStack(cdk.Stack):

    def __init__(self,
        scope: Construct,
        construct_id: str,
        github_org: str,
        github_repo_name: str,
        github_branch: str,
        deploy_env: str,
        aws_github_provider_arn: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        if aws_github_provider_arn == "":
            provider = iam.OpenIdConnectProvider(self, "Provider",
                url = "https://token.actions.githubusercontent.com",
                client_ids = ["sts.amazonaws.com"]
                )
        else:
            provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
                self,
                "ExistingProvider",
                aws_github_provider_arn)


        principal = iam.OpenIdConnectPrincipal(provider).with_conditions(
            {
            "ForAnyValue:StringLike": {
                "token.actions.githubusercontent.com:sub": [
                    "repo:{0}/{1}:ref:refs/heads/{2}".format(github_org, github_repo_name, github_branch),
                    "repo:{0}/{1}:environment:{2}".format(github_org, github_repo_name, deploy_env)
                ]
                }
            }
        )

        role = iam.Role(self, 
            "DeploymentRole",
            assumed_by=principal,
            description="Grants Github Actions to access AWS",
            managed_policies = [
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambda_FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonVPCFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
                ]
            )