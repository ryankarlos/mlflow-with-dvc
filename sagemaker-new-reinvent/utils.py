import logging
import boto3
from botocore.exceptions import ClientError
from logging import getLogger
import time


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


def delete_pipeline_and_model(model_package_group_name: str, pipeline_name: str):
    sm_client = boto3.client("sagemaker")
    sm_client.delete_pipeline(
        PipelineName=pipeline_name,
    )
    model_package_list = sm_client.list_model_packages(
        ModelPackageGroupName=model_package_group_name
    )
    for version in range(0, len(model_package_list["ModelPackageSummaryList"])):
        sm_client.delete_model_package(
            ModelPackageName=model_package_list["ModelPackageSummaryList"][version]["ModelPackageArn"]
        )
    sm_client.delete_model_package_group(
        ModelPackageGroupName=model_package_group_name
    )


def delete_experiment(experiment_name: str, trial_name: str):
    sm_client = boto3.client("sagemaker")
    components_in_trial = sm_client.list_trial_components(TrialName=trial_name)
    logger.info('TrialComponentNames:')
    for component in components_in_trial['TrialComponentSummaries']:
        component_name = component['TrialComponentName']
        logger.info(f"\t{component_name}")
        sm_client.disassociate_trial_component(TrialComponentName=component_name, TrialName=trial_name)
        try:
            # comment out to keep trial components
            sm_client.delete_trial_component(TrialComponentName=component_name)
        except:
            # component is associated with another trial
            continue
        # to prevent throttling
        time.sleep(.5)
    sm_client.delete_trial(TrialName=trial_name)
    try:
        sm_client.delete_experiment(ExperimentName=experiment_name)
        logger.info(f"\nExperiment {experiment_name} deleted")
    except:
        # experiment already existed and had other trials
        logger.info(f"\nExperiment {experiment_name} in use by other trials. Will not delete")