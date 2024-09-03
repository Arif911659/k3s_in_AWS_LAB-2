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
        "Name": "my-vpc-for-k3s"  # Replace "my-vpc-name" with the desired name
    }
)


# Add public subnet
public_subnet = ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.10.1.0/24",
    map_public_ip_on_launch=True,  # Typically True for public subnets
    availability_zone="ap-southeast-1a",  # Use a valid availability zone
    tags={
        "Name": "public-subnet",
    }
)

# Add private subnet
private_subnet = ec2.Subnet('private-subnet',
    vpc_id=vpc.id,
    cidr_block='10.10.2.0/24',  # Adjusted to avoid overlap with public subnet
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
        "Name": "my-igw"  # Replace with your desired IGW name
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
eip = ec2.Eip('nat-eip', vpc=True)


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







""" """An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws 
import pulumi_aws.ec2 as ec2
from pulumi_aws.ec2 import SecurityGroupRuleArgs


# Configuration
config = pulumi.Config() 
instance_type = 't2.micro' 
ami = "ami-01811d4912b4ccb26"


# Add vpc
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.10.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": "my-vpc-name"  # Replace "my-vpc-name" with the desired name
        }
    )


# Add public_subnet
public_subnet = ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.10.1.0/24",
    map_public_ip_on_launch=False, 
    availability_zone="ap-southeast-1a",  # Use a valid availability zone
    tags={
        "Name": "public-subnet",
    }
)

# Add private_subnet
private_subnet = ec2.Subnet('private-subnet',
    vpc_id=vpc.id,
    cidr_block='10.0.2.0/24',
    map_public_ip_on_launch=False, 
    availability_zone='ap-southeast-1a',
    tags={
        "Name": "private_subnet",
    }
)


# Adding the Internet Gateway with a Name tag
igw = ec2.InternetGateway("Internet-Gateway",
    vpc_id=vpc.id,
    tags={
        "Name": "my-igw"  # Replace with your desired IGW name
    }
)

# Create Route Table
public_route_table = ec2.RouteTable("public_route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0", 
        "gateway_id": igw.id,
    }],
)
# Associate Route Table with Public Subnet

public_route_table_association = ec2.RouteTableAssociation('public-route-table-association',
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id
)


# Elastic IP for NAT Gateway 
eip = ec2.Eip('nat-eip', vpc=True)


# NAT Gateway
nat_gateway= ec2.NatGateway(
    'nat-gateway',
    subnet_id=public_subnet.id, 
    allocation_id=eip.id
) 


# Route Table for Private Subnet 
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
) """

""" # Create Security Group
security_group = aws.ec2.SecurityGroup("web-secgrp",
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
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[
        {
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
        }],
)


# Create instances in the VPC and subnet
ami_id = "ami-01811d4912b4ccb26" # Replace with a valid AMI ID for your region
instance_type = "t3.small"


# Read the public key from the environment (set by GitHub Actions).
public_key = os.getenv("PUBLIC_KEY")

# Create the EC2 KeyPair using the public key 
key_pair = aws.ec2.KeyPair("my-key-pair",
    key_name="my-key-pair", 
    public_key=public_key)

# Create instances for Master-Node
master_node = aws.ec2.Instance("master-node",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    associate_public_ip_address=True,  # Automatically assigns a public IP
    key_name=key_pair.key_name, # Replace with a valid key_pair.key_name
    vpc_security_group_ids=[security_group.id],
    tags={
    "Name": "master-node"
})

# Create worker node 1
worker_node_1 = aws.ec2.Instance("worker-node-1",
    instance_type=instance_type,
    ami=ami_id,  						# Replace with the desired AMI ID
    subnet_id=public_subnet.id,     	# Ensure this is the public subnet
    associate_public_ip_address=True,   # Automatically assigns a public IP
    vpc_security_group_ids=[security_group.id],  	 # Add security groups as needed
    key_name=key_pair.key_name,  					 # Replace with your SSH key pair name
    tags={
        "Name": "worker-node-1"
    }
)

# Create worker node 2
worker_node_2 = aws.ec2.Instance("worker-node-2",
    instance_type=instance_type,
    ami=ami_id,  						# Replace with the desired AMI ID
    subnet_id=public_subnet.id,     	# Ensure this is the public subnet
    associate_public_ip_address=True,   # Automatically assigns a public IP
    vpc_security_group_ids=[security_group.id],  	 # Add security groups as needed
    key_name=key_pair.key_name,  					 # Replace with your SSH key pair name
    tags={
        "Name": "worker-node-2"
    }
) """

""" # Create Nginx instance
nginx_instance = aws.ec2.Instance("nginx-instance", 
	instance_type=instance_type,
	ami=ami,
	subnet_id=public_subnet.id,
	key_name=key_pair.key_name,
	vpc_security_group_ids=[security_group.id],
	tags={
		"Name": "nginx-instance"
	}
)
 """

# Export outputs
""" pulumi.export("master_public_ip", master_node.public_ip)
pulumi.export("worker1_public_ip", worker_node_1.public_ip)
pulumi.export("worker2_public_ip", worker_node_2.public_ip)
pulumi.export("nginx_instance", nginx_instance.public_ip) """


