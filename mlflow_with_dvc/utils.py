import logging
import boto3
from botocore.exceptions import ClientError
from dvc.api import DVCFileSystem
from pathlib import Path
from logging import getLogger

DVC_DIR = str(Path().resolve().parent)


logger = getLogger('utils')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region.

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    Args:
        bucket_name: Bucket to create
        region: String region to create bucket in, e.g., 'us-west-2'

    Returns:
        True if bucket created, else False
    """

    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            s3_client.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True


def list_existing_s3_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    # Output the bucket names
    logger.info(f'Existing buckets:\n {", ".join(buckets)}')


def list_all_tracked_files(dvc_only=True):
    # opening a local repository
    fs = DVCFileSystem(DVC_DIR)
    if dvc_only:
        tracked_list = fs.find('.', detail=False, dvc_only=dvc_only)
    else:
        tracked_list = fs.find(".", detail=False)
    logger.info(f"tracked files: {tracked_list}")


create_bucket('dvc-storage-s3', region='us-east-1')
list_existing_s3_buckets()