
#### Instructions on running mlflow and dvc pipeline

```bash
pip intall poetry
```

Install dependencies from poetry lock file

```bash
poetry install
```

Then run the pipeline script to track a new run.  These will be saved in
a new folder with tracking id in runs folder.

**NOTE**: Specified folder needs to be created during execution when  
referenced for the first time. If it is created upfront, the script  
terminates with the following error message: mlflow.exceptions.MlflowException:
`Could not find experiment with ID 0`. This is set as `runs` folder in root of repo
in the code

```bash
poetry run python -m mlflow_with_dvc.pipeline
```

You should see the output as below

```bash
INFO:__main__:Elasticnet model (alpha=0.500000, l1_ratio=0.500000):
INFO:__main__:RMSE: 0.447125790081536
INFO:__main__:MAE: 0.36150258728645435
INFO:__main__:R2: 0.7044956342219149
Successfully registered model 'ElasticnetWineModel'.
2023/06/22 00:00:21 INFO mlflow.tracking._model_registry.client: Waiting up to 300 seconds for model version to finish creation. Model name: ElasticnetWineModel, version 1
Created version '1' of model 'ElasticnetWineModel'.
```


Run mlflow ui repository root to loads the corresponding runs in `runs` folder for viewing in tracking ui.


```sh
export RUNS=<path-to-runs-folder>
poetry run mlflow ui --backend-store-uri $RUNS \
          --default-artifact-root $RUNS \
          --host 0.0.0.0 \
          --port 5000
```

You should see the server start

```bash
[2023-06-22 00:05:44 +0100] [60920] [INFO] Starting gunicorn 20.1.0
[2023-06-22 00:05:44 +0100] [60920] [INFO] Listening at: http://0.0.0.0:5000 (60920)
[2023-06-22 00:05:44 +0100] [60920] [INFO] Using worker: sync
[2023-06-22 00:05:44 +0100] [60925] [INFO] Booting worker with pid: 60925
[2023-06-22 00:05:44 +0100] [60926] [INFO] Booting worker with pid: 60926
[2023-06-22 00:05:44 +0100] [60927] [INFO] Booting worker with pid: 60927
[2023-06-22 00:05:44 +0100] [60928] [INFO] Booting worker with pid: 60928
```

![](data/images/ui-table.png)
![](data/images/ui-metrics-diff-runs.png)