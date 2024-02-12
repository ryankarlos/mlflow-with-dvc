
#### Sagemaker new features after reinvent 2023

This repo contains source code for the following new Sagemaker features post reinvent 2023:

1 . Sagemaker Step Decorator 
    I have written a blog on this for the AWS Community Builders Developer Experience Month https://community.aws/content/2bFfwOMvMaWfOuwUy30HMF1qgGb/sagemaker.
    The `shipping_catboost_reg` folder contains the source code for the pipeline and steps. The associated notebook 
    run in Sagemaker is also located in the `shipping_catboost_reg` folder.
    - for testing script locally (outside sagemaker), install dependencies with poetry (`poetry install`) and then
run `poetry run python -m sm_examples.shipping_catboost_reg.steps` from root of the repo
   - notebook to uplaod and run in Sagemaker notebook: notebooks/shipping_catboost_reg/demo.ipynb. 
Install dependencies in kernel  `pip install -r ./requirements.txt` and then run all cells
   - Navigate to Sagemaker Studio and you should see the result of the pipeline executions, artifacts and the logs

![pipeline_executons_studio.png](screenshots%2Fpipeline_executons_studio.png)
![pipeline_step_logs_outputs.png](screenshots%2Fpipeline_step_logs_outputs.png)