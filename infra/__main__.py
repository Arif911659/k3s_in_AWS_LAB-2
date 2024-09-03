"""An AWS Python Pulumi program"""

import pulumi
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
private_subnet = ec2.Subnet('private-subnet',
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
eip = ec2.Eip('nat-eip', 
    vpc=True,
    domain="my-vpc",  # Explicitly setting the domain attribute to "vpc"
)
# eip = ec2.Eip('nat-eip', 
#     vpc=True  # Use 'vpc' without setting 'domain'
# )

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

# (Optional) Output the IDs of created resources
pulumi.export('vpc_id', vpc.id)
pulumi.export('public_subnet_id', public_subnet.id)
pulumi.export('private_subnet_id', private_subnet.id)
pulumi.export('igw_id', igw.id)
pulumi.export('nat_gateway_id', nat_gateway.id)
