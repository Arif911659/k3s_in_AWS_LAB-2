"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws 
import pulumi_aws.ec2 as ec2
from pulumi_aws.ec2 import SecurityGroupRuleArgs


# Configuration
config = pulumi.Config() 
instance_type = 't3.small' 
ami "ami-01811d4912b4ccb26"

# Add vpc
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.10.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": "my-vpc-name"  # Replace "my-vpc-name" with the desired name
        }
    )