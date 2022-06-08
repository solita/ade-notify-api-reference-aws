import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as _ec2
)
from constructs import Construct


class VpcStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cidr_range: str,
        stack_log_level: str,
        from_vpc_name=None,
        ** kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        if from_vpc_name is not None:
            self.vpc = _ec2.Vpc.from_lookup(
                self, "vpc",
                vpc_name=from_vpc_name
            )
        else:
            self.vpc = _ec2.Vpc(
                self,
                "VPC",
                cidr=cidr_range,
                max_azs=2,
                nat_gateways=1,
                enable_dns_support=True,
                enable_dns_hostnames=True,
                subnet_configuration=[
                    _ec2.SubnetConfiguration(
                        name="public", cidr_mask=24, subnet_type=_ec2.SubnetType.PUBLIC
                    ),
                    _ec2.SubnetConfiguration(
                        name="private", cidr_mask=24, subnet_type=_ec2.SubnetType.PRIVATE_WITH_NAT
                    )
                ]
            )

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        cdk.CfnOutput(
            self,
            id="VpcID",
            value=self.vpc.vpc_id,
            description="VPC ID",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:vpc-id"
        )

    # properties to share with other stacks
    @property
    def get_vpc(self):
        return self.vpc

    @property
    def get_vpc_public_subnet_ids(self):
        return self.vpc.select_subnets(
            subnet_type=_ec2.SubnetType.PUBLIC
        ).subnet_ids

    @property
    def get_vpc_private_subnet_ids(self):
        return self.vpc.select_subnets(
            subnet_type=_ec2.SubnetType.PRIVATE
        ).subnet_ids
