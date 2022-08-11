import json
import io
import boto3
import base64
from botocore.exceptions import ClientError
import logging
import yaml

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_config_file_aws(config_bucket, config_file_location):
    """Reads configuration file from S3 bucket.
    Args:
        config_bucket (str): Configuration bucket name.
        config_file_location (str): Path to configuration file.
    Returns:
        config (dict): Config file in dictionary.
    """
    s3 = boto3.client('s3')

    data_stream = io.BytesIO()

    try:
        s3.download_fileobj(config_bucket, config_file_location, data_stream)
    except Exception as e:
        raise Exception(e)

    data_stream.seek(0)

    file_format = config_file_location.split('.')

    if file_format[-1] == 'json':
        config = json.load(data_stream)
    elif file_format[-1] == 'yaml':
        config = yaml.load(data_stream, Loader=yaml.FullLoader)

    return config


def get_secret(secret_name):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    secret = None

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])

    return json.loads(secret)