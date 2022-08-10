import json
import os
import aws_notify_api as aws_nf
from adenotifier import notifier
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Compares file url and configuration to identify configured data sources
# Returns list of matched sources
def identify_sources(file_url: str, config: object):
    sources = []
    
    for source in config:
        source_path = source['id']
        
        # Optional attribute
        if ('file_extension' in source['attributes']):
            source_extension = source['attributes']['file_extension']
        else:
            source_extension = ""

        if (source_path in file_url and source_extension in file_url):
            sources.append(source)

    return sources

def lambda_handler(event, context):
    secret_name = os.environ['SECRET_NAME']
    secrets = aws_nf.get_secret(secret_name)

    base_url = secrets["url"]
    notify_api_key = secrets["notify_api_key"]
    notify_api_secret_key = secrets["notify_api_secret_key"]

    config_bucket = os.environ['CONFIG_BUCKET']
    config_file_location = os.environ['CONFIG_FILE_LOCATION']

    config = aws_nf.get_config_file_aws(config_bucket, config_file_location)

    for record in event['Records']: 
        body = json.loads(record['body'])

        for s3_record in body['Records']:
            source_bucket = s3_record['s3']['bucket']['name']
            source_key = s3_record['s3']['object']['key']
            file_url = f's3://{source_bucket}/{source_key}'

            # Identify data sources
            sources = identify_sources(file_url, config)

            # Manifests
            for source in sources:
                logger.info('Processing source: {0}'.format(source['id']))
                notifier.add_to_manifest(
                    file_url, 
                    source, 
                    base_url, 
                    notify_api_key, 
                    notify_api_secret_key)