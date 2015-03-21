#!/usr/bin/python
from __future__ import print_function

import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from sklearn import (
    cross_validation,
    ensemble,
    linear_model,
    metrics,
    neighbors,
    svm,
    tree,
)

from cv_clf import CvClf

# cross validation parameters
K = 5
CV = False

# number of ensemble selection
MAX_IT = 50
OUT_FILENAME = 'mse50_1000.csv'
TEST_FILENAME = 'data/kaggle_test_wc.csv'
TRAIN_FILENAME = 'data/kaggle_train_wc.csv'
TRAIN_SIZE = 3000

def select_ensemble(gs, y, max_it):
    counter = Counter()
    sum_gs = np.zeros(len(y), np.int)

    for it in range(max_it):
        best_i = None
        best_error = float("inf")

        # Finds the best clf to add.
        for i in range(len(gs)):
            # Computes the mode. Defaults to 0 if tied.
            g = (sum_gs + gs[i]) / float(it + 1)
            error = metrics.mean_squared_error(g, y)
            if (error < best_error):
                best_error = error
                best_i = i

        sum_gs += gs[best_i]
        counter[best_i] += 1

    g = sum_gs > max_it / 2
    score = metrics.accuracy_score(g, y)
    print(score)

    return counter

def ReadTrainSet(filename, shuffle=True):
    reader = csv.reader(open(filename, 'r'))
    next(reader)  # Skips header.
    data = np.array(list(reader), dtype=int)
    if shuffle:
        np.random.shuffle(data)
    return data[:, 1:-1], data[:, -1]

def ReadTestSet(filename):
    reader = csv.reader(open(TEST_FILENAME, 'r'))
    next(reader)
    data = np.array(list(reader), dtype=int)
    return data[:, 1:]

def WriteTestGuess(filename, g_test):
    out_file = open(OUT_FILENAME, 'w')
    out_file.write('Id,Prediction\n')
    for i in range(len(g_test)):
        out_file.write('%d,%d\n' % (i + 1, g_test[i]))

class ClassifierSet:
    def __init__(self, x_train, y_train, x_valid, y_valid):
        self.x_train = x_train
        self.y_train = y_train
        self.x_valid = x_valid
        self.y_valid = y_valid
        self.clfs = []
        self.g_valids = []
        self.descs = []

    def Add(self, clf, desc):
        if CV:
            new_clf = CvClf(clf, K)
            new_clf.fit(self.x_train, self.y_train)
        else:
            new_clf = clf.fit(self.x_train, self.y_train)

        self.clfs.append(new_clf)

        g_valid = new_clf.predict(self.x_valid)
        self.g_valids.append(g_valid)

        desc = '%s %f' % (desc, metrics.accuracy_score(g_valid, self.y_valid))
        self.descs.append(desc)
        print(desc)

    def SelectEnsemble(self):
        self.counter = select_ensemble(self.g_valids, self.y_valid, MAX_IT)

        for pair in self.counter.most_common(10):
            weight = float(pair[1]) / MAX_IT
            print("%f %s" % (weight, self.descs[pair[0]]))

    def Train(self, x_full, y_full):
        for i in self.counter:
            print("Full Fit %s" % self.descs[i])
            if CV:
                self.clfs[i].fit(x_full, y_full)
            else:
                self.clfs[i] = self.clfs[i].fit(x_full, y_full)

    def Predict(self, x_test):
        sum_g_tests = np.zeros(len(x_test), np.int)
        for i in self.counter:
            print("Test Predict %s" % self.descs[i])
            sum_g_tests += self.clfs[i].predict(x_test) * self.counter[i]
        return sum_g_tests > MAX_IT / 2

def main():
    # Reads the training set.
    x_full, y_full = ReadTrainSet(TRAIN_FILENAME)
    x_train, y_train = x_full[:TRAIN_SIZE], y_full[:TRAIN_SIZE]
    x_valid, y_valid = x_full[TRAIN_SIZE:], y_full[TRAIN_SIZE:]

    # Trains classifiers on the training set.
    clf_set = ClassifierSet(x_train, y_train, x_valid, y_valid)
    for max_depth in range(3, 5):
        clf_set.Add(ensemble.GradientBoostingClassifier(
            max_depth=max_depth,
            n_estimators=1000,
        ), '%s %d' % ('GradientBoostingClassifier', max_depth))
    for n_estimators in range(500, 501):
        clf_set.Add(ensemble.AdaBoostClassifier(n_estimators=n_estimators),
            '%s %d' % ('AdaBoostClassifier', n_estimators))
    for log_C in [.1 * j for j in range(-40, 40, 10)]:
        clf_set.Add(svm.SVC(C=10**log_C),
            '%s %f' % ('SVC', 10**log_C))
    for criterion in ['gini', 'entropy']:
        for min_samples_leaf in range(1, 25, 1):
            clf_set.Add(tree.DecisionTreeClassifier(
                criterion=criterion,
                min_samples_leaf=min_samples_leaf,
            ), '%s %s min_samples_leaf %d' % ('DecisionTreeClassifier',
                criterion, min_samples_leaf))
        for max_depth in range(1, 8, 1):
            clf_set.Add(tree.DecisionTreeClassifier(
                criterion=criterion,
                max_depth=max_depth,
            ), '%s %s max_depth %d' % ('DecisionTreeClassifier',
                criterion, max_depth))
    for log_C in [.1 * j for j in range(-60, 40, 2)]:
        clf_set.Add(svm.LinearSVC(C=10**log_C),
            '%s %f' % ('LinearSVC', 10**log_C))
    for n_neighbors in range(1, 16, 2):
        clf_set.Add(neighbors.KNeighborsClassifier(n_neighbors=n_neighbors),
            '%s %d' % ('KNeighborsClassifier', n_neighbors))
    for n_estimators in range(60, 200, 10):
        clf_set.Add(ensemble.RandomForestClassifier(n_estimators=n_estimators),
            '%s %d' % ('RandomForestClassifier', n_estimators))
    for log_alpha in [.1 * j for j in range(-30, 30, 2)]:
        clf_set.Add(linear_model.SGDClassifier(alpha=10**log_alpha),
            '%s %f' % ('SGDClassifier', 10**log_alpha))
    for log_alpha in [.1 * j for j in range(-30, 30, 2)]:
        clf_set.Add(linear_model.RidgeClassifier(alpha=10**log_alpha),
            '%s %f' % ('RidgeClassifier', 10**log_alpha))
    for n_iter in range(10, 200, 10):
        clf_set.Add(linear_model.PassiveAggressiveClassifier(n_iter=n_iter),
            '%s %d' % ('PassiveAggressiveClassifier', n_iter))
    for n_estimators in range(5, 200, 10):
        clf_set.Add(ensemble.ExtraTreesClassifier(n_estimators=n_estimators),
            '%s %d' % ('ExtraTreesClassifier', n_estimators))

    # Selects models and trains.
    clf_set.SelectEnsemble()
    clf_set.Train(x_full, y_full)

    x_test = ReadTestSet(TEST_FILENAME)
    g_test = clf_set.Predict(x_test)
    print(sum(g_test))

    WriteTestGuess(OUT_FILENAME, g_test)
    print("Saved as %s" % OUT_FILENAME)

if __name__ == "__main__":
    main()
