import numpy as np

from pyreal.benchmark.challenges.explainer_challenge import ExplainerChallenge
from pyreal.explainers import ShapFeatureImportance


class ShapFeatureImportanceChallenge(ExplainerChallenge):
    def create_explainer(self):
        return ShapFeatureImportance(model=self.dataset.model, x_train_orig=self.dataset.X,
                                     transforms=self.dataset.transforms, fit_on_init=True)

    def evaluate_variation(self, results):
        # TODO: consider alternative evaluation approaches
        return np.max(np.var(results, axis=0))
