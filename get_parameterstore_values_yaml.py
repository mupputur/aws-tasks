import boto3
import yaml
aws_region="ap-south-1"
ssm = boto3.client("ssm",region_name=aws_region)


def get_ssm_secret(parameter_name):
    parameter = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    data = yaml.dump(parameter, open("Oracle_info.yaml", "w"))
    return data


if __name__ == "__main__":
    get_ssm_secret("Oracle")
