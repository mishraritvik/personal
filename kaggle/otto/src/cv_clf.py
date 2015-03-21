#!/usr/bin/python

from __future__ import print_function

import numpy as np
from sklearn import (cross_validation, metrics)

class CvClf(object):
    """
    Wrapper for sklearn classifiers. Can train with cross validation then
    predict using the mean of the trained classifiers.
    """

    def __init__(self, clf, k):
        if k < 2:
            print('cv_clf error: k must be at least 2')
        self.k = k
        self.clf = clf
        self.clfs = []
        self.cv_scores = []

    def fit(self, X, y):
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.int)

        kf = cross_validation.KFold(len(X), n_folds=self.k)

        for train, valid in kf:
            X_train, y_train = X[train], y[train]
            X_valid, y_valid = X[valid], y[valid]
            clf = self.clf.fit(X_train, y_train)
            self.clfs.append(clf)
            self.cv_scores.append(
                metrics.mean_squared_error(y_valid, clf.predict(X_valid)))

    def predict(self, x):
        if not self.clfs:
            print('cv_clf error: not fitted yet')

        gs = []
        mean_gs = np.zeros(len(x), np.int)

        # use trained clfs to predict on test set
        for clf in self.clfs:
            gs.append(clf.predict(x))

        # find mean of all predictions
        for i in range(len(x)):
            new_g = 0
            for j in range(self.k):
                new_g += gs[j][i]
            mean_gs[i] = float(new_g) / float(self.k)

        return mean_gs
