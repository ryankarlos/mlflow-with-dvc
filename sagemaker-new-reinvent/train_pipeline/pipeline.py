
from sagemaker.workflow.pipeline import Pipeline


def pipeline():

    # Create a Sagemaker Pipeline.
    # Each parameter for the pipeline must be set as a parameter explicitly when the pipeline is created.
    # Also pass in each of the steps created above.
    # Note that the order of execution is determined from each step's dependencies on other steps,
    # not on the order they are passed in below.
    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[
            training_instance_type,
            processing_instance_type,
            processing_instance_count,
            input_data,
            model_approval_status,
            training_epochs,
            accuracy_mse_threshold,
        ],
        steps=[step_process, step_train_model, step_evaluate_model, step_cond],
    )