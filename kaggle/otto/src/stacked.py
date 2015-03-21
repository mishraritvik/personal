from sklearn import (
    tree,
    svm,
    ensemble,
    linear_model,
    cross_validation,
    metrics)

data_type = 'tf_idf'
# data_type = 'wc'

def mode(seqs):
    ret = []
    if len(seqs) == 1:
        return seqs[0]
    for i in range(len(seqs[0])):
        total = 0
        for j in range(len(seqs)):
            total += seqs[j][i]
        if total > float(len(seqs)) / 2.0:
            ret.append(1)
        else:
            ret.append(0)
    return ret

# read data
f = open('data/kaggle_train_' + data_type + '.csv')
words = f.readline()

x, y = [], []

for line in f:
    row = line.split(',')
    row = [float(i) for i in row]
    new_x = row[1 : len(row) - 1]
    new_y = row[-1]
    x.append(new_x)
    y.append(new_y)
f.close()

print('data read')

x_train, y_train = x[:3000], y[:3000]
x_test, y_test = x[3000:], y[3000:]

clfs = []

# create ensemble of models

for i in range(1000):
    clf = tree.DecisionTreeClassifier(
        criterion='gini',
        max_depth=2
        )
    sub_x, unused, sub_y, unused = cross_validation.train_test_split(
        x_train,
        y_train,
        test_size=0.5)
    clf = clf.fit(sub_x, sub_y)
    clfs.append(clf)
print('finished stub forest')

for i in range(5, 50):
    clf = tree.DecisionTreeClassifier(
        criterion='gini',
        max_depth=i
        )
    clf = clf.fit(x_train, y_train)
    clfs.append(clf)
print('finished gini depth')

for i in range(10, 300, 30):
    clf = tree.DecisionTreeClassifier(
        criterion='gini',
        min_samples_leaf=i
        )
    clf = clf.fit(x_train, y_train)
    clfs.append(clf)
print('finished gini leaf')

for i in range(5, 50):
    clf = tree.DecisionTreeClassifier(
        criterion='entropy',
        max_depth=i
        )
    clf = clf.fit(x_train, y_train)
    clfs.append(clf)
print('finished entropy depth')

for i in range(10, 300, 30):
    clf = tree.DecisionTreeClassifier(
        criterion='entropy',
        min_samples_leaf=i
        )
    clf = clf.fit(x_train, y_train)
    clfs.append(clf)
print('finished entropy leaf')

for i in [.1 * j for j in range(-10, 30, 5)]:
    clf = svm.LinearSVC(
        penalty='l2',
        loss='l2',
        C=10 ** i)
    clf = clf.fit(x_train, y_train)
    clfs.append(clf)
print('finished linear svm')

cfl = ensemble.BaggingClassifier(
    tree.DecisionTreeClassifier(),
    max_samples=0.5,
    max_features=0.5)
clf = clf.fit(x_train, y_train)
clfs.append(clf)
print('finished bagging')

for i in range(1, 30):
    clf = ensemble.RandomForestClassifier(n_estimators=i)
    clf = clf.fit(x_train, y_train)
    clfs.append(clf)
print('finished random forests')

for i in range(20, 400, 20):
    clf = ensemble.AdaBoostClassifier(n_estimators=i)
    clf = clf.fit(x_train, y_train)
    clfs.append(clf)
print('finished boosting')

print('ensemble training completed, %d models' % len(clfs))

# run all models on all test data
model_results = []
for model in clfs:
    model_results.append(model.predict(x_train))
print('ensemble results calculated')

# transpose data such that each row is the prediction from different models on
# the same data point
stacked_training = []
for i in range(len(model_results[0])):
    xs = []
    for j in range(len(model_results)):
        xs.append(model_results[j][i])
    stacked_training.append(xs)

# do same thing for test data
model_test_results = []
for model in clfs:
    model_test_results.append(model.predict(x_test))

stacked_testing = []
for i in range(len(model_test_results[0])):
    test_xs = []
    for j in range(len(model_test_results)):
        test_xs.append(model_test_results[j][i])
    stacked_testing.append(test_xs)

# train linear model on models
stacked_clfs = []
for i in [.1 * j for j in range(-50, 50, 2)]:
    clf = linear_model.LogisticRegression(
        penalty='l1',
        C=10 ** i)
    clf = clf.fit(stacked_training, y_train)
    stacked_clfs.append(clf)

# calculate new model
stacked_test_acc = []
for clf in stacked_clfs:
    stack_pred = clf.predict(stacked_testing)
    stacked_test_acc.append(metrics.accuracy_score(stack_pred, y_test))

# choose model with best accuracy
best_stack = stacked_clfs[stacked_test_acc.index(min(stacked_test_acc))]
print('best test accuracy achieved: %f' % min(stacked_test_acc))

# run new model on test data
f = open('data/kaggle_test_' + data_type + '.csv')
f_out = open('kaggle_sub.csv', 'w')
words = f.readline()

x = []
for line in f:
    row = line.split(',')
    row = [float(i) for i in row]
    x.append(row[1 :])

# make predictions
final_pred = []
model_test_results = []
for model in clfs:
    model_test_results.append(model.predict(x))

stacked_testing = []
for i in range(len(model_test_results[0])):
    test_xs = []
    for j in range(len(model_test_results)):
        test_xs.append(model_test_results[j][i])
    stacked_testing.append(test_xs)

res = best_stack.predict(stacked_testing)

# create output file
f_out.write('Id,Prediction\n')
for i in range(len(res)):
    f_out.write('%d,%d\n' % (i + 1, res[i]))

f.close()
f_out.close()
