from abc import ABC, abstractmethod

from pyreal.types.explanations.dataframe import (
    AdditiveFeatureContributionExplanation, AdditiveFeatureImportanceExplanation,
    FeatureImportanceExplanation,)


def fit_transformers(transformers, x):
    """
    Fit a set of transformers in-place, transforming the data after each fit. Checks if each
    transformer has a fit function and if so, calls it.
    Args:
        transformers (list of Transformers):
            List of transformers to fit, in order
        x (DataFrame of shape (n_instances, n_features)):
            Dataset to fit on.

    Returns:
        None
    """
    x_transform = x.copy()
    for transformer in transformers:
        fit_func = getattr(transformer, "fit", None)
        if callable(fit_func):
            fit_func(x_transform)
        x_transform = transformer.transform(x_transform)


def run_transformers(transformers, x):
    """
    Run a series of transformers on x_orig

    Args:
        transformers (list of Transformers):
            List of transformers to fit, in order
        x (DataFrame of shape (n_instances, n_features)):
            Dataset to transform

    Returns:
        DataFrame of shape (n_instances, n_features)
            Transformed data
    """
    x_transform = x.copy()
    for transform in transformers:
        x_transform = transform.transform(x_transform)
    return x_transform


class Transformer(ABC):
    """
    An abstract base class for Transformers. Transformers transform data from a first feature space
    to a second, and explanations from the second back to the first.
    """

    def fit(self, x, **params):
        """
        Fit this transformer to data

        Args:
            x (DataFrame of shape (n_instances, n_features)):
                The dataset to fit to
            **params:
                Additional transformer parameters

        Returns:
            None
        """

    @abstractmethod
    def transform(self, x):
        """
        Transform `x` from to a new feature space.
        Args:
            x (DataFrame of shape (n_instances, n_features)):
                The dataset to transform

        Returns:
            DataFrame of shape (n_instances, n_features):
                The transformed dataset
        """

    def fit_transform(self, x, **fit_params):
        """
        Fits this transformer to data and then transforms the same data

        Args:
            x (DataFrame of shape (n_instances, n_features)):
                The dataset to fit and transform
            **fit_params:
                Parameters for the fit function

        Returns:
            The transformed dataset
        """
        self.fit(x, **fit_params)
        return self.transform(x)

    def transform_explanation(self, explanation):
        """
        Transforms the explanation from the second feature space handled by this transformer
        to the first.

        Args:
            explanation (Explanation):
                The explanation to transform

        Returns:
            The transformed explanation
        """
        if isinstance(explanation, AdditiveFeatureContributionExplanation) \
                or isinstance(explanation, AdditiveFeatureImportanceExplanation):
            return self.transform_explanation_additive_contributions(explanation)
        if isinstance(explanation, FeatureImportanceExplanation):
            return self.transform_explanation_feature_importance(explanation)
        raise ValueError("Invalid explanation types %s" % explanation.__class__)

    # noinspection PyMethodMayBeStatic
    def transform_explanation_additive_contributions(self, explanation):
        return explanation

    # noinspection PyMethodMayBeStatic
    def transform_explanation_feature_importance(self, explanation):
        return explanation
