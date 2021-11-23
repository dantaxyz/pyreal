import numpy as np

from pyreal.explainers import Explainer, ShapFeatureImportance


# TODO: modify the following function
def default_explainer(return_contributions=True, return_explainer=False, explainer=None,
                      model=None, x_orig=None, x_train_orig=None,
                      e_algorithm=None, feature_descriptions=None,
                      e_transforms=None, m_transforms=None, i_transforms=None,
                      interpretable_features=True):
    """
    Get a local feature contribution for x_input

    Args:
        return_contributions (Boolean):
            If true, return explanation of features in x_input.
            If true, requires `x_input` and one of `explainer` or (`model and x_train`)
        return_explainer (Boolean):
            If true, return the fitted Explainer object.
            If true, requires one of `explainer` or (`model and x_train`)
        explainer (Explainer):
            Fitted explainer object.
        model (string filepath or model object):
           Filepath to the pickled model to explain, or model object with .predict() function
        x_orig (dataframe of shape (n_instances, x_orig_feature_count)):
           The input to explain
        x_train_orig (dataframe of shape (n_instances, x_orig_feature_count)):
           The training set for the explainer
        e_algorithm (string, one of ["shap"]):
           Explanation algorithm to use. If none, one will be chosen automatically based on model
           type
        feature_descriptions (dict):
           Interpretable descriptions of each feature
        e_transforms (transformer object or list of transformer objects):
           Transformer(s) that need to be used on x_orig for the explanation algorithm:
           x_orig -> x_explain
        m_transforms (transformer object or list of transformer objects):
           Transformer(s) needed on x_orig to make predictions on the dataset with model,
           if different than e_transformers
           x_orig -> x_model
        i_transforms (transformer object or list of transformer objects):
           Transformer(s) needed to make x_orig interpretable
           x_orig -> x_interpret
        interpretable_features (Boolean):
            If True, return explanations using the interpretable feature descriptions instead of
            default names

    Returns:
        Explainer:
            The fitted explainer. Only returned in return_explainer is True
        DataFrame of shape (n_instances, n_features):
            The contribution of each feature. Only returned if return_contributions is True
    """
    if not return_contributions and not return_explainer:
        # TODO: replace with formal warning system
        print("lfc is non-functional with return_contribution and return_explainer set to false")
        return
    if explainer is None and (model is None or x_train_orig is None):
        raise ValueError("lfc requires either explainer OR model and x_train to be passed")
    if return_contributions is True and x_orig is None:
        raise ValueError("return_contributions tag require x_input to be passed")

    if explainer is None:
        explainer = GenericExplainer(model, x_train_orig,
                                             e_algorithm=e_algorithm,
                                             feature_descriptions=feature_descriptions,
                                             e_transforms=e_transforms, m_transforms=m_transforms,
                                             i_transforms=i_transforms,
                                             interpretable_features=interpretable_features,
                                             fit_on_init=True)
    if return_explainer and return_contributions:
        return explainer, explainer.produce(x_orig)
    if return_explainer:
        return explainer
    if return_contributions:
        return explainer.produce(x_orig)


class GenericExplainer(Explainer):
    """
    Unspecified Explainer wrapper.

    A GenericExplainer object assigns a default ML explainer based on the type of x_orig.

    Args:
        model (string filepath or model object):
           Filepath to the pickled model to explain, or model object with .predict() function
        x_train_orig (dataframe of shape (n_instances, x_orig_feature_count)):
           The training set for the explainer
        scope (string of either "global" or "local"):
            Whether the explainer is global or local
        interpretable_features (Boolean):
            If True, return explanations using the interpretable feature descriptions instead of
            default names
        **kwargs: see base Explainer args
    """

    def __init__(self, model, x_train_orig, scope="global", interpretable_features=True, **kwargs):
        self.scope = scope
        self.interpretable_features = interpretable_features
        # TODO: implement smart choosing algorithm based on type of x
        if scope == "global":
            self.base_explainer = ShapFeatureImportance(model, x_train_orig, **kwargs)
        elif scope == "local":
            # TODO: implement default explainer for local
            raise NotImplementedError()
        else:
            raise TypeError("Explainers at this point must be either global or local")
        
        super(GenericExplainer, self).__init__(model, x_train_orig, **kwargs)


    def fit(self):
        """
        Fit this explainer object
        """   
        self.base_explainer.fit()
        

    def produce(self, x_orig):
        """
        Produce the explanation

        Args:
            x_orig (DataFrame of shape (n_instances, n_features)):
                Input to explain

        Returns:
            DataFrame of shape (n_instances, n_features)
                Contribution of each feature for each instance
        """
        return self.base_explainer.produce(x_orig)
