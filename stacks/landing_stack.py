from sys import prefix
import aws_cdk as cdk

from aws_cdk import (
    aws_s3 as _s3,
    aws_s3_notifications as _notify,
    aws_sqs as _sqs)

from constructs import Construct

class LandingStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_log_level: str,
        landing_lifecycle_deletion_days: int,
        landing_bkt_name: str = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Use existing bucket
        #self.landing_bkt = _s3.Bucket.from_bucket_name(
        #    self,
        #    "dataBucket",
        #    bucket_name=landing_bkt_name
        #)

        # Create a new bucket for landing purposes
        self.landing_bkt = _s3.Bucket(
            self,
            "dataBucket",
            versioned=True,
            bucket_name=landing_bkt_name,
            encryption=_s3.BucketEncryption.KMS_MANAGED,
            block_public_access=_s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                _s3.LifecycleRule(
                    enabled=True,
                    # Delete files after defined days
                    expiration=cdk.Duration.days(landing_lifecycle_deletion_days),
                    id=f'delete-after-{landing_lifecycle_deletion_days}-days'
                )
            ]
        )

        self.dead_letter_queue = _sqs.Queue(
            self,
            "DLQ",
            retention_period=cdk.Duration.days(2)
            )

        self.notify_queue = _sqs.Queue(
            self,
            "NotifierQueue",
            visibility_timeout=cdk.Duration.seconds(120),
            dead_letter_queue= _sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.dead_letter_queue
            )
        )

        event = self.landing_bkt.add_event_notification(
            _s3.EventType.OBJECT_CREATED,
            _notify.SqsDestination(self.notify_queue)
        )
