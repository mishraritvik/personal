from sklearn import (tree, svm, ensemble, metrics)

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
f = open('data/kaggle_train_wc.csv')
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

clf = ensemble.BaggingClassifier(
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

# now select models
selected_models = []
model_results = []
prev_acc = float(max([y_test.count(1), y_test.count(0)])) / float(len(y_test))

# run all models on all test data
for model in clfs:
    model_results.append(model.predict(x_test))
print('ensemble results calculated')

while True:
    best_acc, best_model = -1, -1
    # go through all models, see what adding that model does to training acc
    for i in range(len(clfs)):
        if i in selected_models:
            continue
        new_ensemble = []
        for j in selected_models + [i]:
            new_ensemble.append(model_results[j])
        new_acc = metrics.accuracy_score(mode(new_ensemble), y_test)
        if new_acc > max([best_acc, prev_acc]):
            best_acc = new_acc
            new_model = i
    if best_acc != -1:
        selected_models.append(new_model)
        prev_acc = best_acc
        print('model %d added, new accuracy: %f' % (i, prev_acc))
    else:
        break

print('best test accuracy achieved: %f' % prev_acc)

f = open('data/kaggle_test_wc.csv')
f_out = open('kaggle_sub.csv', 'w')
words = f.readline()

x = []
for line in f:
    row = line.split(',')
    row = [float(i) for i in row]
    x.append(row[1 :])

# make predictions
final_pred = []
for model in selected_models:
    final_pred.append(clfs[model].predict(x))
res = mode(final_pred)

# create output file
f_out.write('Id,Prediction\n')
for i in range(len(res)):
    f_out.write('%d,%d\n' % (i + 1, res[i]))

f.close()
f_out.close()
