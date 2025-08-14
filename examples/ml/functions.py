import multiprocessing as mp

import lightgbm as lgb
import numpy as np
from joblib import dump, load
from numpy.linalg import eig
from sklearn.base import BaseEstimator

from flexecutor import StageContext


class MergedLGBMClassifier(BaseEstimator):
    def __init__(self, model_list):
        assert isinstance(model_list, list)

        self.model_list = model_list

    def predict(self, X):
        pred_list = []

        for m in self.model_list:
            pred_list.append(m.predict(X))

        # Average the predictions
        averaged_preds = sum(pred_list) / len(pred_list)

        return averaged_preds

    def save_model(self, model_path):
        dump(self, model_path)

    @staticmethod
    def load_model(model_path):
        return load(model_path)


def pca(ctx: StageContext):
    import logging
    logging.info("Starting PCA function")
    
    [training_data_path] = ctx.get_input_paths("training-data")
    logging.info(f"Training data path: {training_data_path}")

    logging.info("Loading training data")
    train_data = np.genfromtxt(training_data_path, delimiter="\t")
    logging.info(f"Training data shape: {train_data.shape}")
    
    train_labels = train_data[:, 0]
    a = train_data[:, 1 : train_data.shape[1]]
    logging.info(f"Feature matrix shape: {a.shape}")
    
    logging.info("Computing mean")
    ma = np.mean(a.T, axis=1)
    logging.info("Computing centered matrix")
    ca = a - ma
    logging.info("Computing covariance matrix")
    va = np.cov(ca.T)
    logging.info("Computing eigenvalues and eigenvectors")
    values, vectors = eig(va)
    logging.info("Computing principal components")
    pa = vectors.T.dot(ca.T)
    logging.info(f"Principal components shape: {pa.shape}")

    vectors_pca_path = ctx.next_output_path("vectors-pca")
    training_data_transform = ctx.next_output_path("training-data-transform")
    np.savetxt(vectors_pca_path, vectors, delimiter="\t")
    first_n_a = pa.T[:, 0:100].real
    train_labels = train_labels.reshape(train_labels.shape[0], 1)
    first_n_a_label = np.concatenate((train_labels, first_n_a), axis=1)
    np.savetxt(training_data_transform, first_n_a_label, delimiter="\t")


def train(
    io,
    task_id,
    process_id,
    feature_fraction,
    max_depth,
    num_of_trees,
    chance,
    training_path,
):
    import logging
    logging.info(f"Starting train function for process {process_id}")
    
    logging.info(f"Loading training data from {training_path}")
    train_data = np.genfromtxt(training_path, delimiter="\t")
    logging.info(f"Training data shape: {train_data.shape}")
    
    y_train = train_data[0:5000, 0]
    x_train = train_data[0:5000, 1 : train_data.shape[1]]
    logging.info(f"X_train shape: {x_train.shape}, y_train shape: {y_train.shape}")

    _id = str(task_id) + "_" + str(process_id)
    logging.info(f"Training model with ID: {_id}")
    params = {
        "boosting_type": "gbdt",
        "objective": "multiclass",
        "num_classes": 10,
        "metric": {"multi_logloss"},
        "num_leaves": 50,
        "learning_rate": 0.05,
        "feature_fraction": feature_fraction,
        "bagging_fraction": chance,  # If model indexes are 1->20, this makes feature_fraction: 0.7->0.9
        "bagging_freq": 5,
        "max_depth": max_depth,
        "verbose": -1,
        "num_threads": 2,
    }

    lgb_train = lgb.Dataset(x_train, y_train)
    gbm = lgb.train(
        params,
        lgb_train,
        num_boost_round=num_of_trees,
        valid_sets=lgb_train,
        # early_stopping_rounds=5
    )

    y_pred = gbm.predict(x_train, num_iteration=gbm.best_iteration)
    # accuracy = calc_accuracy(y_pred, y_train)

    return gbm


def train_with_multiprocessing(ctx: StageContext):
    import logging
    logging.info("Starting train_with_multiprocessing function")
    
    # Use sequential processing instead of multiprocessing to avoid container issues
    task_id = 0
    num_models = 4  # Number of models to train sequentially
    logging.info(f"Training {num_models} models sequentially")
    
    param = {"feature_fraction": 1, "max_depth": 8, "num_of_trees": 30, "chance": 1}
    logging.info(f"Training parameters: {param}")

    training_data_paths = ctx.get_input_paths("training-data-transform")
    training_data_path = training_data_paths[0]
    logging.info(f"Training data path: {training_data_path}")

    logging.info("Training models sequentially")
    for i in range(num_models):
        logging.info(f"Training model {i+1}/{num_models}")
        result = train(
            ctx,
            task_id,
            i,
            param["feature_fraction"],
            param["max_depth"],
            param["num_of_trees"],
            param["chance"],
            training_data_path,
        )
        model_path = ctx.next_output_path("models")
        result.save_model(model_path)
        logging.info(f"Model {i+1} saved to {model_path}")


def calc_accuracy(y_pred, y_train):
    count_match = 0
    for i in range(len(y_pred)):
        result = np.where(y_pred[i] == np.amax(y_pred[i]))[0]
        if result == y_train[i]:
            count_match = count_match + 1
    # The accuracy on the training set
    accuracy = count_match / len(y_pred)
    return accuracy


def aggregate(ctx: StageContext):
    import logging
    logging.info("Starting aggregate function")
    
    training_data_paths = ctx.get_input_paths("training-data-transform")
    training_data_path = training_data_paths[0]
    model_paths = ctx.get_input_paths("models")
    logging.info(f"Processing {len(model_paths)} models")

    # Load test data more efficiently
    logging.info("Loading test data")
    test_data = np.genfromtxt(training_data_path, delimiter="\t")
    y_test = test_data[5000:, 0]
    x_test = test_data[5000:, 1 : test_data.shape[1]]
    logging.info(f"Test data shape: x_test={x_test.shape}, y_test={y_test.shape}")
    
    # Load models without storing them all in memory at once
    model_list = []
    for i, model_path in enumerate(model_paths):
        logging.info(f"Loading model {i+1}/{len(model_paths)}")
        model = lgb.Booster(model_file=model_path)
        model_list.append(model)

    # Merge models
    logging.info("Creating merged forest")
    forest = MergedLGBMClassifier(model_list)
    forest_path = ctx.next_output_path("forests")
    forest.save_model(forest_path)
    logging.info(f"Forest saved to {forest_path}")

    # Predict efficiently
    logging.info("Making predictions")
    y_pred = forest.predict(x_test)
    acc = calc_accuracy(y_pred, y_test)
    logging.info(f"Accuracy: {acc}")
    
    prediction_path = ctx.next_output_path("predictions")
    np.savetxt(prediction_path, y_pred, delimiter="\t")
    logging.info(f"Predictions saved to {prediction_path}")

    # Clean up memory
    del model_list
    del forest
    del test_data
    del x_test
    del y_test
    del y_pred
    
    return acc


def test(ctx: StageContext):
    import logging
    logging.info("Starting test function")
    
    predictions_paths = ctx.get_input_paths("predictions")
    logging.info(f"Processing {len(predictions_paths)} prediction files")
    
    predictions = []
    for i, prediction_path in enumerate(predictions_paths):
        logging.info(f"Loading predictions {i+1}/{len(predictions_paths)}")
        pred = np.genfromtxt(prediction_path, delimiter="\t")
        predictions.append(pred)
    
    test_paths = ctx.get_input_paths("training-data-transform")
    test_path = test_paths[0]
    logging.info(f"Loading test data from {test_path}")
    test_data = np.genfromtxt(test_path, delimiter="\t")

    y_test = test_data[5000:, 0]
    logging.info(f"Test labels shape: {y_test.shape}")
    
    # Average predictions
    logging.info("Computing averaged predictions")
    y_pred = sum(predictions) / len(predictions)
    acc = calc_accuracy(y_pred, y_test)
    logging.info(f"Final accuracy: {acc}")

    accuracy_path = ctx.next_output_path("accuracies")
    with open(accuracy_path, "w") as f:
        f.write("My accuracy is: " + str(acc))
    logging.info(f"Accuracy saved to {accuracy_path}")
    
    # Clean up memory
    del predictions
    del test_data
    del y_test
    del y_pred
