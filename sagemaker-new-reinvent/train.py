import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

if __name__ == "__main__":
    training_data_directory = "/opt/ml/input/data/train"
    train_features_data = os.path.join(training_data_directory, "train_features.csv")
    train_labels_data = os.path.join(training_data_directory, "train_labels.csv")
    print("Reading input data")
    X_train = pd.read_csv(train_features_data, header=None)
    y_train = pd.read_csv(train_labels_data, header=None)

    model = LogisticRegression(class_weight="balanced", solver="lbfgs")
    print("Training LR model")
    model.fit(X_train, y_train)
    model_output_directory = os.path.join("/opt/ml/model", "model.joblib")
    print("Saving model to {}".format(model_output_directory))
    joblib.dump(model, model_output_directory)

    sklearn.fit({"train": preprocessed_training_data})
    training_job_description = sklearn.jobs[-1].describe()
    model_data_s3_uri = "{}{}/{}".format(
        training_job_description["OutputDataConfig"]["S3OutputPath"],
        training_job_description["TrainingJobName"],
        "output/model.tar.gz",
    )