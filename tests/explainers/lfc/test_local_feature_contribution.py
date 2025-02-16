import numpy as np
import pandas as pd

from pyreal.explainers import LocalFeatureContribution


def test_produce_with_renames(regression_one_hot):
    model = regression_one_hot
    transforms = model["transformers"]
    feature_descriptions = {"A": "Feature A", "B": "Feature B"}
    lfc = LocalFeatureContribution(
        model=model["model"],
        x_train_orig=model["x"],
        e_algorithm="shap",
        fit_on_init=True,
        transformers=transforms,
        interpretable_features=True,
        feature_descriptions=feature_descriptions,
    )
    x_one_dim = pd.DataFrame([[2, 10, 10]], columns=["A", "B", "C"])

    contributions = lfc.produce(x_one_dim).get()
    assert x_one_dim.shape == contributions.shape
    assert abs(contributions["Feature A"][0] + 1) < 0.0001
    assert abs(contributions["Feature B"][0]) < 0.0001
    assert abs(contributions["C"][0]) < 0.0001


def test_evaluate_variation(classification_no_transforms):
    model = classification_no_transforms
    lfc = LocalFeatureContribution(
        model=model["model"],
        x_train_orig=model["x"],
        e_algorithm="shap",
        transformers=model["transformers"],
        fit_on_init=True,
        classes=np.arange(1, 4),
    )

    # Assert no crash. Values analyzed through benchmarking
    lfc.evaluate_variation(with_fit=False, n_iterations=5)
    lfc.evaluate_variation(with_fit=True, n_iterations=5)


def test_produce_with_renames_with_size(regression_one_hot):
    model = regression_one_hot
    transforms = model["transformers"]
    feature_descriptions = {"A": "Feature A", "B": "Feature B"}
    lfc = LocalFeatureContribution(
        model=model["model"],
        x_train_orig=model["x"],
        e_algorithm="shap",
        fit_on_init=True,
        transformers=transforms,
        interpretable_features=True,
        feature_descriptions=feature_descriptions,
        training_size=2,
    )
    x_one_dim = pd.DataFrame([[2, 10, 10]], columns=["A", "B", "C"])

    contributions = lfc.produce(x_one_dim).get()
    assert x_one_dim.shape == contributions.shape


def test_evaluate_variation_with_size(classification_no_transforms):
    model = classification_no_transforms
    lfc = LocalFeatureContribution(
        model=model["model"],
        x_train_orig=model["x"],
        e_algorithm="shap",
        transformers=model["transformers"],
        fit_on_init=True,
        training_size=4,
        classes=np.arange(1, 4),
    )

    # Assert no crash. Values analyzed through benchmarking
    lfc.evaluate_variation(with_fit=False, n_iterations=5)
    lfc.evaluate_variation(with_fit=True, n_iterations=5)
