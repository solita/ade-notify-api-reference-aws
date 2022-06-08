import aws_cdk as cdk

from aws_cdk import (
    aws_s3 as _s3,
    aws_s3_deployment as _s3_deploy)

from constructs import Construct

class ConfigurationStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_log_level: str,
        configuration_bkt_name: str = None,
        config_file_local_path: str = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.configuration_bkt = _s3.Bucket(
            self,
            "dataBucket",
            versioned=True,
            bucket_name=configuration_bkt_name,
            encryption=_s3.BucketEncryption.KMS_MANAGED
        )

        upload_files = _s3_deploy.BucketDeployment(
            self,
            "DeployBucket",
            destination_bucket=self.configuration_bkt,
            sources=[_s3_deploy.Source.asset(config_file_local_path)]
        )

