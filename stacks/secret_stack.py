import aws_cdk as cdk
from aws_cdk import (
    aws_secretsmanager as secretsmanager)
from constructs import Construct

class SecretStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_log_level: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.secret = secretsmanager.Secret(self, "Secret")