from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.pipeline import Pipeline
from sagemaker import get_execution_role
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
)
from sagemaker.workflow.function_step import step

# run below in notebook (sagemaker)
# !sudo chmod 777 lost+found


def initialise_session_and_params():
    pipeline_session = PipelineSession()
    region = pipeline_session.boto_region_name
    default_bucket = pipeline_session.default_bucket()
    input_path = f"s3://{default_bucket}/canvas/sample_dataset/canvas-sample-shipping-logs.csv"
    # Set path to config file
    os.environ["SAGEMAKER_USER_CONFIG_OVERRIDE"] = os.getcwd()

    instance_count = ParameterInteger(
        name="InstanceCount",
        default_value=1
    )

    instance_type = ParameterString(
        name="InstanceType",
        default_value='ml.m5.large'
    )
    return input_path, instance_count, instance_type


def run_pipeline(input_path, instance_count, instance_type):
    categorical_features_names = ['ShippingPriority', 'ShippingOrigin', 'InBulkOrder', 'Carrier']
    delayed_data = step(preprocess, name="ShippingPreprocess")(input_path)
    delayed_model = step(train, name="ShippingTrain")(train_df=delayed_data[0],
                                                      validation_df=delayed_data[1],
                                                      categorical_features_names=categorical_features_names)
    delayed_evaluation_result = step(evaluate, name="ShippingEval")(model=delayed_model,
                                                                  test_df=delayed_data[2])

    steps = [delayed_evaluation_result]

    pipeline = Pipeline(
        name="ShippingPipeline",
        parameters=[
            instance_count,
            instance_type,
        ],
        steps=steps,
        sagemaker_session=pipeline_session
    )
    role = sagemaker.get_execution_role()
    pipeline.upsert(role_arn=role)
    execution = pipeline.start()