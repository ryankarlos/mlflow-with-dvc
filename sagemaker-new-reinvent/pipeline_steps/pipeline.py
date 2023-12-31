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

#
# @step
# def preprocess():
#     num_rows = 5000
#     rng = np.random.default_rng(seed=7)
#     buildings_data = {
#     "sqft": rng.exponential(scale=1000, size=num_rows),
#     "year": rng.integers(low=1995, high=2023, size=num_rows),
#
#     "building_type": rng.choice(["A", "B", "C"], size=num_rows)
#     }
#     buildings_lazy = pl.LazyFrame(buildings_data)
#     lazy_query = (buildings_lazy.with_columns(
#         (pl.col("price") / pl.col("sqft")).alias("price_per_sqft")
#     ).filter(pl.col("price_per_sqft") > 100).filter(pl.col("year") < 2010)
#                   )
#     lazy_query.show_graph()
#     return  lazy_query.collect()
#
#
#
# @step
# def train(training_data):
#     return trained_model
#
#
# @step(name="evaluate")
# def evaluate_model():
#     # code to evaluate the model
#     return {
#         "rmse": rmse_value
#     }
#
#
# @step(name="register")
# def register_model():
#     # code to register the model
#     ...
#
#
# conditionally_register = ConditionStep(
#     name="conditional_register",
#     conditions=[
#         ConditionGreaterThanOrEqualTo(
#             # Output of the evaluate step must be json serializable
#             left=evaluate_model()["rmse"],  #
#             right=5,
#         )
#     ],
#     if_steps=[FailStep(name="Fail", error_message="Model performance is not good enough")],
#     else_steps=[register_model()],
# )
#
#
# pipeline = Pipeline(
#     name="<pipeline-name>",
#     steps=[step_train_result],
#     sagemaker_session=<sagemaker-session>,
# )
#
# step_process_result = preprocess()
# step_train_result = train(step_process_result)
# get_step(step_train_result).add_depends_on(step_process_result)


import boto3
import sagemaker
from sagemaker.remote_function import remote

sm_session = sagemaker.Session(boto_session=boto3.session.Session(region_name="us-east-1"))
settings = dict(
    sagemaker_session=sm_session,
    role="",
    instance_type="ml.m5.xlarge",
    dependencies='./requirements.txt'
)

@remote(**settings)
def divide(x, y):
    return x / y


if __name__ == "__main__":
    print(divide(2, 3.0))

