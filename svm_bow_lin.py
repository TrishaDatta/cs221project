import csv
import numpy as np
from sklearn import svm
from sklearn.svm import SVC
from sklearn.metrics import precision_recall_fscore_support
from util import get_final_lists

f = open('data/train_vocab_5.txt', 'r')
vocab = f.read().splitlines()

f = open('data/train_classes_5.txt', 'r')
train_labels = f.read().splitlines()
train_labels = [int(label) for label in train_labels]

train_set = []
with open('data/train_bag_of_words_5.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        train_set.append([int(i) for i in row])

f = open('data/test_classes_0.txt', 'r')
test_labels = f.read().splitlines()
test_labels = [int(label) for label in test_labels]

test_set = []
with open('data/test_bag_of_words_0.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        test_set.append([int(i) for i in row])

train_labels, train_set, test_labels, test_set = get_final_lists(train_labels, train_set, test_labels, test_set)
        
           
clf = SVC(kernel='linear')
clf.fit(np.array(train_set), np.array(train_labels))




predictions = clf.predict(np.array(test_set))
correct = 0
print('predictions', predictions)
tp = 0
tn = 0
fn = 0
fp = 0
for i in range(len(predictions)):
    if predictions[i] == test_labels[i]:
        correct += 1
    label = predictions[i]
    if label == 1 and test_labels[i] == 1:
        tp += 1
    elif label == 1 and test_labels[i] == 0:
        fp += 1
    elif label == 0 and test_labels[i] == 1:
        fn += 1
    elif label == 0 and test_labels[i] == 0:
        tn += 1

print('accuracy', correct / len(predictions))

print('accuracy', (tp + tn) / (tp + tn + fp + fn))
precision = tp / (tp + fp)
print('precision', precision)
recall = tp / (tp + fn)
print('recall', recall)
print("f1", 2 * recall * precision / (recall + precision))

print(precision_recall_fscore_support(test_labels, predictions))

imp = clf.coef_.tolist()[0]
coefs = [abs(x) for x in imp]

coefs = sorted(zip(coefs, vocab), reverse=True)
for i in range(10):
    print(coefs[i])
