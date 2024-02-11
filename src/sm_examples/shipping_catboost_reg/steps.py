import pandas as pd
import numpy as np
import os
from catboost import CatBoost, CatBoostRegressor, Pool
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import sagemaker
import os



def preprocess(raw_data):
    df = pd.read_csv(raw_data)
    df.drop(['ProductId', 'OrderID', 'OnTimeDelivery', 'OrderDate'], axis=1, inplace=True)
    train, test = train_test_split(df, test_size=0.2)
    train, validation = train_test_split(train, test_size=0.2)
    print("Completed running the processing job")
    return pd.DataFrame(train), pd.DataFrame(validation), pd.DataFrame(test)



def train(
    train_df,
    validation_df,
    categorical_features_names,
    target = "ExpectedShippingDays",
    iterations=100,
    learning_rate=0.01,
    n_estimators=4000,
):
    y_train = train_df.loc[:, target]
    train_df.drop([target], axis=1, inplace=True)
    y_validation = validation_df.loc[:, target]
    validation_df.drop([target], axis=1, inplace=True)
    train_pool = Pool(train_df, label=y_train, cat_features=categorical_features_names)
    val_pool = Pool(validation_df, label=y_validation, cat_features=categorical_features_names)
    model = CatBoostRegressor(custom_metric= ['R2', 'RMSE'], learning_rate=learning_rate, n_estimators=n_estimators)
    model.fit(train_pool, eval_set=val_pool, verbose=2000, plot=True)
    return model



def evaluate(model, test_df,target = "ExpectedShippingDays",):
    y_test = test_df.loc[:, target]
    test_df.drop([target], axis=1, inplace=True)
    predictions = model.predict(test_df)

    mse = mean_squared_error(y_test, predictions)
    std = np.std(y_test - predictions)
    report_dict = {
        "regression_metrics": {
            "mse": {"value": mse, "standard_deviation": std},
        },
    }
    return report_dict


if __name__ == "__main__":
    from pathlib import Path

    csv_path = str(Path(__file__).parents[3] / "notebooks/shipping_catboost_reg/canvas-sample-shipping-logs.csv")
    print(csv_path)
    train_df, val_df, test_df = preprocess(csv_path)
    categorical_features_names = ['ShippingPriority', 'ShippingOrigin', 'InBulkOrder', 'Carrier']
    model = train(train_df, val_df, categorical_features_names)
    report = evaluate(model, test_df)
    print(f"evaluation report: {report}")