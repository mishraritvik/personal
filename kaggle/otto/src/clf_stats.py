#!/usr/bin/python
from __future__ import print_function

import csv
import numpy as np
import sys

# from collections import (Counter, defaultdict)
from itertools import groupby
from sklearn import (
    cross_validation,
    ensemble,
    linear_model,
    neighbors,
    svm,
    tree,
)

# Specify K for K-fold cross validation.
K = 5

# Specify input and output files.
OUT_FILENAME = 'clf_stats.txt'
TRAIN_FILENAME = 'data/kaggle_train_wc.csv'

def ReadTrainSet(filename, shuffle=True):
    reader = csv.reader(open(filename, 'r'))
    next(reader)  # Skips header.
    data = np.array(list(reader), dtype=int)
    if shuffle:
        np.random.shuffle(data)
    return data[:, 1:-1], data[:, -1]

class ClassifierEvaluator:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.clfs = []
        self.descs = []

    def Add(self, clf, desc):
        self.descs.append(desc)
        self.clfs.append(clf)

    def Analyze(self, k):
        clf_scores = {}
        for i, clf in enumerate(self.clfs):
            print('Analyzing', clf, file=sys.stderr)
            clf_scores[self.descs[i]] = cross_validation.cross_val_score(
                clf, self.X, self.y, cv=k, scoring='accuracy', n_jobs=k).mean()
        return clf_scores


def main():
    # Reads the training set.
    X, y = ReadTrainSet(TRAIN_FILENAME)
    print('Data read.')

    # Evaluates classifiers with K-fold cross-validation.
    clf_evaluator = ClassifierEvaluator(X, y)

    for max_depth in range(3, 5):
        clf_evaluator.Add(ensemble.GradientBoostingClassifier(
            max_depth=max_depth,
            n_estimators=1000,
        ), '%s %d' % ('GradientBoostingClassifier', max_depth))
    for n_estimators in range(300, 601, 50):
        clf_evaluator.Add(
            ensemble.AdaBoostClassifier(n_estimators=n_estimators),
            '%s %d' % ('AdaBoostClassifier', n_estimators))
    for log_C in [.1 * j for j in range(-40, 40, 10)]:
        clf_evaluator.Add(svm.SVC(C=10**log_C),
            '%s %f' % ('SVC', 10**log_C))
    for criterion in ['gini', 'entropy']:
        for min_samples_leaf in range(1, 25, 1):
            clf_evaluator.Add(tree.DecisionTreeClassifier(
                criterion=criterion,
                min_samples_leaf=min_samples_leaf,
            ), '%s %s min_samples_leaf %d' % ('DecisionTreeClassifier',
                criterion, min_samples_leaf))
        for max_depth in range(1, 8, 1):
            clf_evaluator.Add(tree.DecisionTreeClassifier(
                criterion=criterion,
                max_depth=max_depth,
            ), '%s %s max_depth %d' % ('DecisionTreeClassifier',
                criterion, max_depth))
    for log_C in [.1 * j for j in range(-60, 40, 2)]:
        clf_evaluator.Add(svm.LinearSVC(C=10**log_C),
            '%s %f' % ('LinearSVC', 10**log_C))
    for n_neighbors in range(1, 16, 2):
        clf_evaluator.Add(neighbors.KNeighborsClassifier(n_neighbors=n_neighbors),
            '%s %d' % ('KNeighborsClassifier', n_neighbors))
    for n_estimators in range(60, 200, 10):
        clf_evaluator.Add(ensemble.RandomForestClassifier(n_estimators=n_estimators),
            '%s %d' % ('RandomForestClassifier', n_estimators))
    for log_alpha in [.1 * j for j in range(-30, 30, 2)]:
        clf_evaluator.Add(linear_model.SGDClassifier(alpha=10**log_alpha),
            '%s %f' % ('SGDClassifier', 10**log_alpha))
    for log_alpha in [.1 * j for j in range(-30, 30, 2)]:
        clf_evaluator.Add(linear_model.RidgeClassifier(alpha=10**log_alpha),
            '%s %f' % ('RidgeClassifier', 10**log_alpha))
    for n_iter in range(10, 200, 10):
        clf_evaluator.Add(linear_model.PassiveAggressiveClassifier(n_iter=n_iter),
            '%s %d' % ('PassiveAggressiveClassifier', n_iter))
    for n_estimators in range(5, 200, 10):
        clf_evaluator.Add(ensemble.ExtraTreesClassifier(n_estimators=n_estimators),
            '%s %d' % ('ExtraTreesClassifier', n_estimators))

    clf_scores = clf_evaluator.Analyze(K)

    out = open(OUT_FILENAME, 'w')
    out.write('Scores for classifiers with {}-fold cross validation\n'.format(K))

    # Group the results by classifier.
    for key, group in groupby(sorted(clf_scores), lambda k: k.split()[0]):
        # Then arrange in decreasing order of score within a classifier.
        for clf in sorted(group, key=lambda clf: clf_scores[clf], reverse=True):
            out.write('{}\t{}\n'.format(clf, clf_scores[clf]))

    print("Saved as %s" % OUT_FILENAME)

if __name__ == "__main__":
    main()
