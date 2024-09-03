"""An AWS Python Pulumi program"""

import pulumi
import os 
import pulumi_aws as aws 
import pulumi_aws.ec2 as ec2
from pulumi_aws.ec2 import SecurityGroupRuleArgs


# Configuration
config = pulumi.Config() 
instance_type = 't2.micro' 
ami = "ami-01811d4912b4ccb26"


# Add VPC
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.10.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": "my-vpc"
    }
)


# Add public subnet
public_subnet = ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.10.1.0/24",
    map_public_ip_on_launch=True,  # Typically True for public subnets
    availability_zone="ap-southeast-1a",
    tags={
        "Name": "public-subnet",
    }
)

# Add private subnet
private_subnet = ec2.Subnet("private-subnet",
    vpc_id=vpc.id,
    cidr_block='10.10.2.0/24',
    map_public_ip_on_launch=False, 
    availability_zone='ap-southeast-1a',
    tags={
        "Name": "private-subnet",
    }
)


# Adding the Internet Gateway with a Name tag
igw = ec2.InternetGateway("Internet-Gateway",
    vpc_id=vpc.id,
    tags={
        "Name": "my-igw"
    }
)

# Create Route Table for the public subnet
public_route_table = ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0", 
        "gateway_id": igw.id,
    }],
)

# Associate Route Table with the Public Subnet
public_route_table_association = ec2.RouteTableAssociation('public-route-table-association',
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id
)


# Elastic IP for NAT Gateway 
# eip = ec2.Eip('nat-eip', 
#     vpc=True,
#     domain="my-vpc",  # Explicitly setting the domain attribute to "vpc"
# )
eip = ec2.Eip('nat-eip', 
    vpc=True  # Use 'vpc' without setting 'domain'
)

# NAT Gateway
nat_gateway = ec2.NatGateway(
    'nat-gateway',
    subnet_id=public_subnet.id, 
    allocation_id=eip.id
) 


# Route Table for the Private Subnet 
private_route_table = ec2.RouteTable(
    'private-route-table', 
    vpc_id=vpc.id, 
    routes=[{
        'cidr_block': '0.0.0.0/0', 
        'nat_gateway_id': nat_gateway.id,
    }]
)

# Associate the private route table with the private subnet 
private_route_table_association = ec2.RouteTableAssociation(
    'private-route-table-association', 
    subnet_id=private_subnet.id, 
    route_table_id=private_route_table.id
)

# Create Security Group for allowing SSH and k3s traffic
security_group = aws.ec2.SecurityGroup("k3s-secgrp",
    description='Enable SSH and K3s access',
    vpc_id=vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["0.0.0.0/0"],       #[vpc.cidr_block], #Allow port to vpc-cidr
        },
    ],
    egress=[
        {
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
        }],
    tags={
        "Name": "k3s-secgrp"
    }
)

# Read the public key from the environment (set by GitHub Actions).
public_key = os.getenv("PUBLIC_KEY")

# Create the EC2 KeyPair using the public key 
key_pair = aws.ec2.KeyPair("my-key-pair",
    key_name="my-key-pair", 
    public_key=public_key)


git_runner_instance = ec2. Instance('git-runner-instance', 
    instance_type=instance_type,
    ami=ami,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name=key_pair.key_name,
    tags={
        'Name': 'Git-Runner-Dev',
        }
)


# (Optional) Output the IDs of created resources
pulumi.export('git_runner_public_ip', git_runner_instance.public_ip)
