import boto3

class AWSEC2:
    def __init__(self, **config):
        self.region = config.get('region')
        self.zone = config.get('zone')
        self.key_name = config.get('key_name')
        self.client = boto3.client('ec2', self.region)
        self.resource = boto3.resource('ec2', self.region)
        self.secGroup = None
        self.vpc = None
        self.igId = None
        self.routeTable = None
        self.subnet = None

    def create_keypair(self):
        try:
            key_pair = self.client.create_key_pair(KeyName=self.key_name)
            return key_pair
        except Exception as e:
            print(f"Already existing key pair:{e}")

    def create_vpc(self, cidrBlock, vpcName):
        vpc_init = self.client.create_vpc(CidrBlock=cidrBlock)
        vpc = self.resource.Vpc(vpc_init["Vpc"]["VpcId"])
        vpc.create_tags(Tags=[{"Key": "Name", "Value": vpcName}])
        vpc.wait_until_available()
        self.vpc = vpc
        return vpc

    def create_internet_gateway(self, ig_name):
        ig_init = self.client.create_internet_gateway(
            TagSpecifications=[
                {'ResourceType': 'internet-gateway',
                 'Tags': [{"Key": "Name", "Value": ig_name}]}, ]
        )
        igId = ig_init["InternetGateway"]["InternetGatewayId"]
        self.vpc.attach_internet_gateway(InternetGatewayId=igId)
        self.igId = igId
        return igId

    def create_route_table(self, rt_name):
        routeTable = self.vpc.create_route_table()
        route = routeTable.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=self.igId
        )
        routeTable.create_tags(Tags=[{"Key": "Name", "Value": rt_name}])
        self.routeTable = routeTable
        return route

    def create_subnet(self, subnet_cidr, sn_name):
        subnet = self.vpc.create_subnet(
            CidrBlock=subnet_cidr, AvailabilityZone="{}{}".format(self.region, self.zone))
        subnet.create_tags(Tags=[{"Key": "Name", "Value": sn_name}])
        self.routeTable.associate_with_subnet(SubnetId=subnet.id)
        self.subnet = subnet
        return subnet

    def create_security_group(self, sg_name):
        secGroup = self.resource.create_security_group(
                GroupName=sg_name, Description='EC2 Security Group', VpcId=self.vpc.id)
        secGroup.authorize_ingress(IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        secGroup.create_tags(Tags=[{"Key": "Name", "Value": sg_name}])
        self.secGroup = secGroup
        return secGroup

    def launch_instance(self, ami, instance_type, ec2_name):
        ec2_Instances = self.resource.create_instances(
            ImageId=ami, InstanceType=instance_type, MaxCount=1, MinCount=1,
            NetworkInterfaces=[{'SubnetId': self.subnet.id, 'DeviceIndex': 0,
                                'AssociatePublicIpAddress': True, 'Groups': [self.secGroup.group_id]}],
            KeyName=self.key_name)
        instance = ec2_Instances[0]
        instance.create_tags(
            Tags=[{"Key": "Name", "Value": ec2_name}])
        instance.wait_until_running()
        print('Instance Id: ', instance.id)
        return instance


if __name__ == "__main__":
    ec2 = AWSEC2(region='ap-south-1', zone='a', key_name='python_key_pair')
    ec2.create_keypair()
    ec2.create_vpc(cidrBlock='192.168.1.0/24', vpcName='python-vpc')
    ec2.create_internet_gateway(ig_name='python-ig')
    ec2.create_route_table(rt_name='python-rt')
    ec2.create_subnet(subnet_cidr='192.168.1.0/24', sn_name='python-sn')
    ec2.create_security_group(sg_name='python-SG')
    ec2.launch_instance(ami='ami-074dc0a6f6c764218',instance_type='t2.micro',ec2_name='python-instances')
