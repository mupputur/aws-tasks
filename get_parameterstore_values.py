import boto3

ssm = boto3.client("ssm")

def get_ssm_secret(parameter_name):
    parameter = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return parameter


if __name__ == "__main__":
    data = get_ssm_secret("Oracle")
    print(data.get("Parameter").get("Value"))
    print(data)