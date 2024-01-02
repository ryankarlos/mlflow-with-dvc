
from sagemaker.workflow.pipeline import Pipeline
from .steps import *
import json

from sagemaker.workflow.parameters import ParameterInteger, ParameterString, ParameterFloat



def pipeline():
    # raw input data
    input_data = ParameterString(name="InputData", default_value=raw_s3)

    # status of newly trained model in registry
    model_approval_status = ParameterString(name="ModelApprovalStatus", default_value="Approved")

    # processing step parameters
    processing_instance_type = ParameterString(
        name="ProcessingInstanceType", default_value="ml.m5.xlarge"
    )
    processing_instance_count = ParameterInteger(name="ProcessingInstanceCount", default_value=1)

    # training step parameters
    training_instance_type = ParameterString(name="TrainingInstanceType", default_value="ml.m5.xlarge")
    training_epochs = ParameterString(name="TrainingEpochs", default_value="100")

    # model performance step parameters
    accuracy_mse_threshold = ParameterFloat(name="AccuracyMseThreshold", default_value=0.75)


    pipeline = Pipeline(
        name="pipeline_demo",
        parameters=[
            training_instance_type,
            processing_instance_type,
            processing_instance_count,
            input_data,
            model_approval_status,
            training_epochs,
            accuracy_mse_threshold,
        ],
        steps=[preprocess_step(), train_step(), evaluation_step(), model_package_step(), register_model_step()]
    )

    return pipeline

if __name__ == "__main__":
    definition = json.loads(pipeline().definition())
    pipeline.upsert(role_arn=role)
    execution = pipeline.start()
    execution.wait()