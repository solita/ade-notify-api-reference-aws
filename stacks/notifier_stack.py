import aws_cdk as cdk

from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_events as _events,
    aws_events_targets as targets,
    aws_logs as logs
    )

from aws_cdk import aws_lambda_python_alpha as _lambdapython
from constructs import Construct
from aws_cdk.aws_lambda_event_sources import SqsEventSource

class NotifierStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc,
        secret,
        sqs_queue,
        config_bucket,
        config_file_bucket_location: str,
        notify_function_name: str,
        manifest_function_name: str,
        notifier_schedule: str,
        sqs_batch_size: int,
        sqs_max_batching_window: int,
        manifester_timeout_sec: int,
        notifier_timeout_sec: int,
        stack_log_level: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        notify_lambda_role = _iam.Role(self, "Lambda Execution role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # Manifester lambda
        lambda_func = _lambdapython.PythonFunction(
            self, 
            'LambdaFunction',
            entry="functions/ade_notify_api",
            runtime=_lambda.Runtime.PYTHON_3_9,
            index="add_to_manifest.py",
            handler='lambda_handler',
            role=notify_lambda_role,
            vpc=vpc,
            timeout=cdk.Duration.seconds(manifester_timeout_sec),
            function_name=manifest_function_name,
            description="Notify API - add to manifest",
            environment={
                    'CONFIG_BUCKET': config_bucket.bucket_name,
                    'SECRET_NAME': secret.secret_arn,
                    'CONFIG_FILE_LOCATION': config_file_bucket_location
                },
            log_retention=logs.RetentionDays.TWO_WEEKS
            )

        # Role grants
        notify_lambda_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        notify_lambda_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        secret.grant_read(notify_lambda_role)
        config_bucket.grant_read_write(notify_lambda_role)

        lambda_func.add_event_source(
            SqsEventSource(
                sqs_queue,
                batch_size=sqs_batch_size,
                max_batching_window=cdk.Duration.minutes(sqs_max_batching_window),
                report_batch_item_failures=True
            )
        )

        # Notifier lambda
        notifier_lambda_func = _lambdapython.PythonFunction(
            self, 
            'LambdaFunction-notifier',
            entry="functions/ade_notify_api",
            runtime=_lambda.Runtime.PYTHON_3_9,
            index="notify.py",
            handler='lambda_handler',
            role=notify_lambda_role,
            vpc=vpc,
            timeout=cdk.Duration.seconds(notifier_timeout_sec),
            function_name=notify_function_name,
            description="Notify API - notify",
            environment={
                    'CONFIG_BUCKET': config_bucket.bucket_name,
                    'SECRET_NAME': secret.secret_arn,
                    'CONFIG_FILE_LOCATION': config_file_bucket_location
                },
            log_retention=logs.RetentionDays.TWO_WEEKS
            )

        # Notifier schedule
        lambda_cw_event = _events.Rule(
            self, 
            "Rule",
            schedule=_events.Schedule.expression(notifier_schedule)
        )

        lambda_cw_event.add_target(targets.LambdaFunction(notifier_lambda_func))
