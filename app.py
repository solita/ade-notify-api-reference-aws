#!/usr/bin/env python3

import aws_cdk as cdk

from stacks.vpc_stack import VpcStack
from stacks.landing_stack import LandingStack
from stacks.configuration_bucket import ConfigurationStack
from stacks.secret_stack import SecretStack
from stacks.notifier_stack import NotifierStack

app = cdk.App()

environment = app.node.try_get_context("env")
build_params = app.node.try_get_context(environment)

# VPC Stack for hosting Secure workloads & Other resources
vpc_stack = VpcStack(
    app,
    f"{app.node.try_get_context('project')}-vpc-stack",
    cidr_range=build_params['cidr_range'],
    stack_log_level="INFO",
    description="VPC for Notify API"
)

# Landing bucket stack
landing_stack = LandingStack(
    app,
    f"{app.node.try_get_context('project')}-landing-stack",
    stack_log_level="INFO",
    landing_lifecycle_deletion_days=build_params['landing_lifecycle_deletion_days'],
    landing_bkt_name=build_params['bucket_name'],
    description="Landing bucket"
)

# Configuration bucket stack
configuration_stack = ConfigurationStack(
    app,
    f"{app.node.try_get_context('project')}-config-bucket-stack",
    stack_log_level="INFO",
    configuration_bkt_name=build_params['configuration_bucket_name'],
    config_file_local_path = build_params['config_file_local_path'],
    description="Configuration bucket"
)

# Secrets stack
secret_stack = SecretStack(
    app,
    f"{app.node.try_get_context('project')}-secrets-stack",
    stack_log_level="INFO",
    description="Notify API secrets"
)

# Notifier stack
notifier_stack = NotifierStack(
    app,
    f"{app.node.try_get_context('project')}-notifier-stack",
    stack_log_level="INFO",
    vpc = vpc_stack.vpc,
    secret = secret_stack.secret,
    sqs_queue = landing_stack.notify_queue,
    config_bucket = configuration_stack.configuration_bkt,
    config_file_bucket_location = build_params['config_file_bucket_location'],
    notify_function_name = f"{app.node.try_get_context('project')}-notify",
    manifest_function_name = f"{app.node.try_get_context('project')}-add-to-manifest",
    notifier_schedule = build_params['notifier_schedule'],
    sqs_batch_size = build_params['sqs_batch_size'],
    sqs_max_batching_window = build_params['sqs_max_batching_window'],
    manifester_timeout_sec = build_params['manifester_timeout_sec'],
    notifier_timeout_sec = build_params['notifier_timeout_sec'],
    description="Notify-API stack"
)

# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            cdk.Tags.of(app).add(
                k, v, apply_to_launched_instances=True, priority=300)

app.synth()
