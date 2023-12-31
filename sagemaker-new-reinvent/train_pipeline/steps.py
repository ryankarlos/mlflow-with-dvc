from sagemaker.workflow.step_outputs import get_step
import numpy as np
import polars as pl
from sagemaker.workflow.function_step import step
from sagemaker.workflow.step_outputs import get_step
from sagemaker.workflow.pipeline import Pipeline
import boto3
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.fail_step import FailStep

from sagemaker.inputs import TrainingInput
from sagemaker.workflow.steps import TrainingStep
from sagemaker.workflow.model_step import ModelStep
import time
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.estimator import SKLearn
import json
from sagemaker.s3 import S3Downloader
from sagemaker.model import Model
from sagemaker.sklearn.model import SKLearnModel
from sagemaker import PipelineModel
from sagemaker.workflow.conditions import ConditionLessThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet
from sagemaker.model_metrics import MetricsSource, ModelMetrics
from sagemaker.workflow.step_collections import RegisterModel


def preprocess_step():
    sklearn_processor = SKLearnProcessor(
        framework_version="0.20.0",
        role="[Your SageMaker-compatible IAM role]",
        instance_type="ml.m5.xlarge",
        instance_count=1,
    )

    processor_args = sklearn_processor.run(
        code="preprocessing.py",
        inputs=[ProcessingInput(source=input_data, destination="/opt/ml/processing/input")],
        outputs=[
            ProcessingOutput(output_name="train_data", source="/opt/ml/processing/train"),
            ProcessingOutput(output_name="test_data", source="/opt/ml/processing/test"),
        ],
        arguments=["--train-test-split-ratio", "0.2"],
    )

    step_process = ProcessingStep(
        name="PreprocessData",
        step_args=processor_args,
    )


def train_step():
    sklearn = SKLearn(
        entry_point="train.py", framework_version="0.20.0", instance_type="ml.m5.xlarge", role=role
    )
    train_args = sklearn.fit({"train": TrainingInput(
        s3_data=step_process.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri,
        content_type="text/csv",
    )})
    step_train_model = TrainingStep(name="TrainTensorflowModel", step_args=train_args)
    model_data_s3_uri = "{}{}/{}".format(
        training_job_description["OutputDataConfig"]["S3OutputPath"],
        training_job_description["TrainingJobName"],
        "output/model.tar.gz",
    )


def evaluation_step():
    sklearn_processor.run(
        code="evaluation.py",
        inputs=[
            ProcessingInput(source=step_train_model.properties.ModelArtifacts.S3ModelArtifacts, destination="/opt/ml/processing/model"),
            ProcessingInput(source=step_process.properties.ProcessingOutputConfig.Outputs["test"].S3Output.S3Uri, destination="/opt/ml/processing/test"),
        ],
        outputs=[ProcessingOutput(output_name="evaluation", source="/opt/ml/processing/evaluation")],
    )
    step_evaluate_model = ProcessingStep(
        name="EvaluateModelPerformance",
        step_args=eval_args,
        property_files=[evaluation_report],
    )


def model_package_step():

    scaler_model_s3 = "{}/model.tar.gz".format(
        step_process.arguments["ProcessingOutputConfig"]["Outputs"][0]["S3Output"]["S3Uri"]
    )
    scaler_model = SKLearnModel(
        model_data=scaler_model_s3,
        role=role,
        sagemaker_session=pipeline_session,
        entry_point="code/preprocess.py",
        framework_version=sklearn_framework_version,
    )
    pipeline_model = PipelineModel(
        models=[scaler_model], role=role, sagemaker_session=pipeline_session
    )

def register_model_step():

    evaluation_s3_uri = "{}/evaluation.json".format(
        step_evaluate_model.arguments["ProcessingOutputConfig"]["Outputs"][0]["S3Output"]["S3Uri"]
    )

    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri=evaluation_s3_uri,
            content_type="application/json",
        )
    )

    register_args = pipeline_model.register(
        content_types=["text/csv"],
        response_types=["text/csv"],
        inference_instances=["ml.m5.large", "ml.m5.xlarge"],
        transform_instances=["ml.m5.xlarge"],
        model_package_group_name=model_package_group_name,
        model_metrics=model_metrics,
        approval_status=model_approval_status,
    )

    step_register_pipeline_model = ModelStep(
        name="PipelineModel",
        step_args=register_args,
    )
