from abc import ABC
from abc import abstractmethod

from real.explainers import Explainer


class LocalFeatureContributionsBase(Explainer, ABC):
    """
    Base class for LocalFeatureContributionsBase explainer objects

    A LocalFeatureContributionsBase object explains a machine learning prediction by assigning an
    importance or contribution score to every feature. LocalFeatureContribution objects explain by
    taking an instance and returning one number per feature, per instance.

    Args:
        model (string filepath or model object):
           Filepath to the pickled model to explain, or model object with .predict() function
        x_orig (dataframe of shape (n_instances, x_orig_feature_count)):
           The training set for the explainer
        e_algorithm (string, one of ["shap"]):
           Explanation algorithm to use. If none, one will be chosen automatically based on model
           type
        contribution_transformers (contribution transformer object(s)):
           Object or list of objects that include .transform_contributions(contributions)
           functions, used to adjust the contributions back to interpretable form.
        interpretable_features (Boolean):
            If True, return explanations using the interpretable feature descriptions instead of
            default names
        **kwargs: see base Explainer args
    """
    def __init__(self, model, x_orig,
                 contribution_transformers=None, interpretable_features=True, **kwargs):
        if contribution_transformers is not None and \
                not isinstance(contribution_transformers, list):
            self.contribution_transformers = [contribution_transformers]
        else:
            self.contribution_transformers = contribution_transformers

        self.interpretable_features = interpretable_features
        super(LocalFeatureContributionsBase, self).__init__(model, x_orig,
                                                            **kwargs)

    @abstractmethod
    def fit(self):
        """
        Fit this explainer object
        """
        pass

    def produce(self, x_orig):
        """
        Produce the local feature contribution explanation

        Args:
            x_orig (DataFrame of shape (n_instances, n_features):
                Input to explain

        Returns:
            DataFrame of shape (n_instances, n_features)
                Contribution of each feature for each instance
        """
        if x_orig.ndim == 1:
            x_orig = x_orig.to_frame().reshape(1, -1)
        if x_orig.shape[1] != self.expected_feature_number:
            raise ValueError("Received input of wrong size."
                             "Expected ({},), received {}"
                             .format(self.expected_feature_number, x_orig.shape))
        contributions = self.get_contributions(x_orig)
        return self.transform_contributions(contributions)

    @abstractmethod
    def get_contributions(self, x_orig):
        """
        Gets the raw contributions. Abstract method.
        Args:
            x_orig (DataFrame of shape (n_instances, n_features):
                Input to explain

        Returns:
            DataFrame of shape (n_instances, n_features)
                Contribution of each feature for each instance
        """
        pass

    def transform_contributions(self, contributions):
        """
        Transform contributions to an interpretable form.

        Args:
            contributions (DataFrame of shape (n_instances, x_explain_feature_count)):
        Returns:
            DataFrame of shape (n_instances, x_interpret_feature_count)
                The transformed contributions
        """
        if self.contribution_transformers is None:
            return contributions
        for transform in self.contribution_transformers:
            contributions = transform.transform_contributions(contributions)
        if self.interpretable_features:
            return self.convert_columns_to_interpretable(contributions)
        return contributions
