import os
from requests import get
import aws_notify_api as aws_nf
from adenotifier import notifier
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Notifies all open manifests from config file.
    Args:
        None.
    Returns:
        None.
    """
    secret_name = os.environ['SECRET_NAME']
    secrets = aws_nf.get_secret(secret_name)

    config_bucket = os.environ['CONFIG_BUCKET']
    config_file_location = os.environ['CONFIG_FILE_LOCATION']

    # Get configuration file (datasource-config/datasources.json)
    config = aws_nf.get_config_file_aws(config_bucket, config_file_location)

    base_url = secrets["url"]
    notify_api_key = secrets["notify_api_key"]
    notify_api_secret_key = secrets["notify_api_secret_key"]

    for key in config:
        source = key

        notifier.notify_manifests(
            source,
            base_url,
            notify_api_key,
            notify_api_secret_key
        )