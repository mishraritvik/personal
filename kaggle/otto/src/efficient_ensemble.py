#!/usr/bin/python

from __future__ import print_function
import csv
import sys

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
    tree
)

MAX_IT = 50
OUT_FILENAME = 'mse50_gb_1000_345.csv'
TEST_FILENAME = 'data/kaggle_test_wc.csv'
TRAIN_FILENAME = 'data/kaggle_train_wc.csv'
TRAIN_SIZE = 3000
MSE = True

def select_ensemble_mode(gs, y, max_it):
    counter = Counter()
    sum_gs = np.zeros(len(y), np.int)

    for it in range(max_it):
        best_i = None
        best_score = float("-inf")

        # Finds the best clf to add.
        for i in range(len(gs)):
            # Computes the mode. Defaults to 0 if tied.
            g = sum_gs + gs[i] > (it + 1) / 2
            score = metrics.accuracy_score(g, y)
            if (score > best_score):
                best_score = score
                best_i = i

        sum_gs += gs[best_i]
        counter[best_i] += 1

    g = sum_gs > max_it / 2
    score = metrics.accuracy_score(g, y)
    print(score)

    return counter

def train_stacked_ensemble(gs, y):
    # TODO: this needs to be done with cross validation

    # Transpose data so that each row is a vector of responses from each x_i.
    stacked_training = (np.array(gs)).transpose()

    # Train Linear SVMs.
    stacked_clfs = []
    for log_C in [.1 * j for j in range(-60, 40, 2)]:
        clf = svm.LinearSVC(
            C=10**log_C,
        )
        clf.fit(stacked_training, y)
        stacked_clfs.append(clf)

    # Find the best stacked clf.
    best_acc = 0
    best_stacked = stacked_clfs[0]
    for clf in stacked_clfs:
        pred = clf.predict(stacked_training)
        score = metrics.accuracy_score(pred, y)
        if score > best_acc:
            best_stacked = clf
            best_acc = score

    print('Best validation accuracy achieved: %f' % best_acc)

    return best_stacked

def predict_stacked_ensemble(stacked_clf, clfs, x):
    # Run ensemble models on test data.
    model_results = []
    for clf in clfs:
        model_results.append(clf.predict(x))

    return stacked_clf.predict(np.array(model_results).transpose())

def select_ensemble(gs, y, max_it):
    counter = Counter()
    sum_gs = np.zeros(len(y), np.int)

    for it in range(max_it):
        best_i = None
        best_error = float("inf")

        # Finds the best clf to add.
        for i in range(len(gs)):
            # Computes the mean label.
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

def main():
    # Check command line argument.
    if (sys.argv[-1] == '--stacked'):
        print('Using Stacked Generalization.')
        MSE = False
    else:
        print('Ensemble Selection with MSE.')

    # Reads the training set.
    reader = csv.reader(open(TRAIN_FILENAME, 'r'))
    next(reader)
    data = np.array(list(reader), dtype=int)
    np.random.shuffle(data)
    x_train = data[:TRAIN_SIZE, 1:-1]
    y_train = data[:TRAIN_SIZE, -1]
    x_valid = data[TRAIN_SIZE:, 1:-1]
    y_valid = data[TRAIN_SIZE:, -1]
    x_full = data[:, 1:-1]
    y_full = data[:, -1]

    # Trains classifiers on the training set.
    clfs = []
    g_valids = []
    descs = []
    for max_depth in range(3, 6, 1):
        clf = ensemble.GradientBoostingClassifier(
            n_estimators=1000,
            max_depth=max_depth,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %d %f' % ('GradientBoostingClassifier', max_depth,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for n_estimators in range(250, 350, 50):
        clf = ensemble.AdaBoostClassifier(
            n_estimators=n_estimators,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %d %f' % ('AdaBoostClassifier', n_estimators,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for criterion in ['gini', 'entropy']:
        for min_samples_leaf in range(1, 25, 1):
            clf = tree.DecisionTreeClassifier(
                criterion=criterion,
                min_samples_leaf=min_samples_leaf,
            )
            clf = clf.fit(x_train, y_train)
            clfs.append(clf)
            g_valid = clf.predict(x_valid)
            g_valids.append(g_valid)
            desc = '%s %s min_samples_leaf %d %f' % ('DecisionTreeClassifier',
                criterion, min_samples_leaf,
                metrics.accuracy_score(g_valid, y_valid))
            descs.append(desc)
            print("Train Fit %s" % (desc))
        for max_depth in range(1, 8, 1):
            clf = tree.DecisionTreeClassifier(
                criterion=criterion,
                max_depth=max_depth,
            )
            clf = clf.fit(x_train, y_train)
            clfs.append(clf)
            g_valid = clf.predict(x_valid)
            g_valids.append(g_valid)
            desc = '%s %s max_depth %d %f' % ('DecisionTreeClassifier',
                criterion, max_depth, metrics.accuracy_score(g_valid, y_valid))
            descs.append(desc)
            print("Train Fit %s" % (desc))
    for log_C in [.1 * j for j in range(-60, 40, 2)]:
        clf = svm.LinearSVC(
            C=10**log_C,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %f %f' % ('LinearSVC', 10**log_C,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for n_neighbors in range(1, 16, 2):
        clf = neighbors.KNeighborsClassifier(
            n_neighbors=n_neighbors,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %d %f' % ('KNeighborsClassifier', n_neighbors,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for n_estimators in range(60, 100, 5):
        clf = ensemble.RandomForestClassifier(
            n_estimators=n_estimators,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %d %f' % ('RandomForestClassifier', n_estimators,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for log_alpha in [.1 * j for j in range(-30, 30, 2)]:
        clf = linear_model.SGDClassifier(
            alpha=10**log_alpha,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %f %f' % ('SGDClassifier', 10**log_alpha,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for log_alpha in [.1 * j for j in range(-30, 30, 2)]:
        clf = linear_model.RidgeClassifier(
            alpha=10**log_alpha,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %f %f' % ('RidgeClassifier', 10**log_alpha,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for n_iter in range(10, 200, 10):
        clf = linear_model.PassiveAggressiveClassifier(
            n_iter=n_iter,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %d %f' % ('PassiveAggressiveClassifier', n_iter,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))
    for n_estimators in range(5, 50, 5):
        clf = ensemble.ExtraTreesClassifier(
            n_estimators=n_estimators,
        )
        clf = clf.fit(x_train, y_train)
        clfs.append(clf)
        g_valid = clf.predict(x_valid)
        g_valids.append(g_valid)
        desc = '%s %d %f' % ('ExtraTreesClassifier', n_estimators,
            metrics.accuracy_score(g_valid, y_valid))
        descs.append(desc)
        print("Train Fit %s" % (desc))

    if MSE:
        # Use Ensemble Selection with Mean Squared Error.
        # Selects classifiers based on the validation set.
        counter = select_ensemble(g_valids, y_valid, MAX_IT)

        # Describes the selected classifiers.
        for pair in counter.most_common(10):
            print("%f %s" % (float(pair[1]) / MAX_IT, descs[pair[0]]))

        # Trains selected classifiers on the full set.
        for i in counter:
            print("Full Fit %s" % descs[i])
            clfs[i] = clfs[i].fit(x_full, y_full)
    else:
        # Use Stacked Generalization.
        stacked_clfs = train_stacked_ensemble(g_valids, y_valid)
        # TODO: remove any models with weights below some threshold

    # Reads the test set.
    reader = csv.reader(open(TEST_FILENAME, 'r'))
    next(reader)
    data = np.array(list(reader), dtype=int)
    x_test = data[:, 1:]

    # Predicts for the test set.
    if MSE:
        sum_g_tests = np.zeros(len(x_test), np.int)
        for i in counter:
            print("Test Predict %s" % descs[i])
            sum_g_tests += clfs[i].predict(x_test) * counter[i]
        g_test = sum_g_tests > MAX_IT / 2
        print(sum(g_test))
    else:
        g_test = predict_stacked_ensemble(stacked_clfs, clfs, x_test)


    # Writes the test set predictions.
    out_file = open(OUT_FILENAME, 'w')
    out_file.write('Id,Prediction\n')
    for i in range(len(g_test)):
        out_file.write('%d,%d\n' % (i + 1, g_test[i]))
    print("Saved as %s" % OUT_FILENAME)

if __name__ == "__main__":
    main()
