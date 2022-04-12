from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from pyreal.explainers import ExplainerBase


class TimeSeriesImportanceBase(ExplainerBase, ABC):
    """
    Base class for time series contributions explainer objects. Abstract class

    A TimeSeriesBase object explains a time-series machine learning classification.

    Args:
        model (string filepath or model object):
           Filepath to the pickled model to explain, or model object with .predict() function
        x_train_orig (dataframe of shape (n_instances, length of series)):
           The training set for the explainer
        **kwargs: see base Explainer args
    """

    def __init__(self, model, x_train_orig, **kwargs):
        super(TimeSeriesImportanceBase, self).__init__(model, x_train_orig, **kwargs)

    @abstractmethod
    def fit(self):
        """
        Fit this explainer object
        """

    def produce(self, x_orig):
        # Importance for a given model stays constant, so can be saved and re-returned
        series = False
        name = None
        if isinstance(x_orig, pd.Series):
            name = x_orig.name
            series = True
            x_orig = x_orig.to_frame().T
        contributions = self.get_contributions(x_orig)
        contributions, x_interpret = self.transform_explanation(contributions, x_orig)
        if series:
            x_interpret = x_interpret.squeeze()
            x_interpret.name = name
        contributions = contributions.get()
        return contributions, x_interpret

    @abstractmethod
    def get_contributions(self, x_orig):
        """
        Get the raw explanation.
        Args:
            x_orig (DataFrame of shape (n_instances, length of series):
                Input to explain

        Returns:
            DataFrame of shape (n_instances, out_features)
                Contribution of each feature for each instance
        """

    def evaluate_variation(self, with_fit=False, explanations=None, n_iterations=20, n_rows=10):
        """
        Evaluate the variation of the explanations generated by this Explainer.
        A variation of 0 means this explainer is expected to generate the exact same explanation
        given the same model and input. Variation is always non-negative, and can be arbitrarily
        high.

        Args:
            with_fit (Boolean):
                If True, evaluate the variation in explanations including the fit (fit each time
                before running). If False, evaluate the variation in explanations of a pre-fit
                Explainer.
            explanations (None or List of DataFrames of shape (n_instances, n_features)):
                If provided, run the variation check on the precomputed list of explanations
                instead of generating
            n_iterations (int):
                Number of explanations to generate to evaluation variation
            n_rows (int):
                Number of rows of dataset to generate explanations on

        Returns:
            float
                The variation of this Explainer's explanations
        """
        if explanations is None:
            explanations = []
            for _ in range(n_iterations - 1):
                if with_fit:
                    self.fit()
                explanations.append(
                    self.produce(self._x_train_orig.iloc[0:n_rows])[0].to_numpy())

        return np.max(np.var(explanations, axis=0))

# The following function is from sktime
# def check_input(X, univariate, to_np, to_pd):
#     """
#     Validate input data.
#     Parameters
#     ----------
#     X : pd.DataFrame or np.array
#         Input data
#     univariate : bool, optional (default=False)
#         Enforce that X is univariate.
#     enforce_min_instances : int, optional (default=1)
#         Enforce minimum number of instances.
#     enforce_min_columns : int, optional (default=1)
#         Enforce minimum number of columns (or time-series variables).
#     to_np : bool, optional (default=False)
#         If True, X will be coerced to a 3-dimensional numpy array.
#     to_pd : bool, optional (default=False)
#         If True, X will be coerced to a nested pandas DataFrame.
#     Returns
#     -------
#     X : pd.DataFrame or np.ndarray
#         Checked and possibly converted input data
#     Raises
#     ------
#     ValueError
#         If X is invalid input data
#     """
#    # check input type
#     if to_np and to_pd:
#         raise ValueError("`to_np` and `to_pd` cannot both be set to True")

#     if not isinstance(X, [pd.DataFrame, np.ndarray]):
#         raise ValueError(
#             f"X must be a pd.DataFrame or a np.array, " f"but found: {type(X)}"
#         )

#     # check np.array
#     # check first if we have the right number of dimensions, otherwise we
#     # may not be able to get the shape of the second dimension below
#     if isinstance(X, np.ndarray):
#         if X.ndim == 2:
#             X = X.reshape(X.shape[0], 1, X.shape[1])
#         elif X.ndim == 1 or X.ndim > 3:
#             raise ValueError(
#                 f"If passed as a np.array, X must be a 2 or 3-dimensional "
#                 f"array, but found shape: {X.shape}"
#             )
#         if coerce_to_pandas:
#             X = from_3d_numpy_to_nested(X)

#     # enforce minimum number of columns
#     n_columns = X.shape[1]
#     if n_columns < enforce_min_columns:
#         raise ValueError(
#             f"X must contain at least: {enforce_min_columns} columns, "
#             f"but found only: {n_columns}."
#         )

#     # enforce univariate data
#     if enforce_univariate and n_columns > 1:
#         raise ValueError(
#             f"X must be univariate with X.shape[1] == 1, but found: "
#             f"X.shape[1] == {n_columns}."
#         )

#     # enforce minimum number of instances
#     if enforce_min_instances > 0:
#         _enforce_min_instances(X, min_instances=enforce_min_instances)

#     # check pd.DataFrame
#     if isinstance(X, pd.DataFrame):
#         if not is_nested_dataframe(X):
#             raise ValueError(
#                 "If passed as a pd.DataFrame, X must be a nested "
#                 "pd.DataFrame, with pd.Series or np.arrays inside cells."
#             )
#         # convert pd.DataFrame
#         if coerce_to_numpy:
#             X = from_nested_to_3d_numpy(X)

#     return X
