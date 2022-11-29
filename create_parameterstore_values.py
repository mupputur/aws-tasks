import boto3


AWS_REGION = "ap-south-1"

ssm_client = boto3.client("ssm", region_name=AWS_REGION)

new_string_parameter = ssm_client.put_parameter(
    Name='EC2_LAUNCH',
    Description='EC2 Instance type for Dev environment',
    Value="ec2 = AWSEC2(region='ap-south-1', zone='a', key_name='python_key_pair')",
    Type='String',
    Overwrite=True,
    Tier='Standard',
    DataType='text')

print(
    f"String Parameter created with version {new_string_parameter['Version']} and Tier {new_string_parameter['Tier']}"
)

