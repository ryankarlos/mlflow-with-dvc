
#### Sagemaker reinvent new services

This repo contains source code for the following:

1 . Sagemaker Step Decorator blog https://community.aws/content/2bFfwOMvMaWfOuwUy30HMF1qgGb/sagemaker
    - for testing script locally (outside sagemaker), install dependencies with poetry (`poetry install`) and then
run `poetry run python -m sm_examples.shipping_catboost_reg.steps` from root of the repo
   - notebook to uplaod and run in Sagemaker notebook: notebooks/shipping_catboost_reg/demo.ipynb. 
Install dependencies in kernel  `pip install -r ./requirements.txt` and then run all cells
   - Navigate to Sagemaker Studio and you should see the result of the pipeline executions, artifacts and the logs

![pipeline_executons_studio.png](screenshots%2Fpipeline_executons_studio.png)
![pipeline_step_logs_outputs.png](screenshots%2Fpipeline_step_logs_outputs.png)