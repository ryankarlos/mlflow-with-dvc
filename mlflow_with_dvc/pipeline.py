import logging
import sys
import warnings
import mlflow.sklearn
import numpy as np
from urllib.parse import urlparse
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_wine
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)
    data = load_wine(as_frame=True)
    df = data['frame']
    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(df)

    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["target"], axis=1)
    test_x = test.drop(["target"], axis=1)
    train_y = train[["target"]]
    test_y = test[["target"]]

    alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    mlflow.set_tracking_uri(str(Path(__file__).parent.parent / 'runs'))
    with mlflow.start_run():
        # Log data params
        mlflow.log_param("data_version", 'v1')
        mlflow.log_param("input_rows", df.shape[0])
        mlflow.log_param("input_columns", df.shape[1])

        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)

        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        logger.info(f"Elasticnet model (alpha={alpha:f}, l1_ratio={l1_ratio:f}):")
        logger.info(f"RMSE: {rmse}")
        logger.info(f"MAE: {mae}")
        logger.info(f"R2: {r2}")

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        # Model registry does not work with file store
        if tracking_url_type_store != "file":
            # Register the model
            mlflow.sklearn.log_model(
                lr, "model", registered_model_name="ElasticnetWineModel"
            )
        else:
            mlflow.sklearn.log_model(lr, "model")
