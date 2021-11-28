import csv
import nltk
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from util import get_final_lists

f = open('data/train_vocab_5.txt', 'r')
vocab = f.read().splitlines()

f = open('data/train_classes_5.txt', 'r')
train_labels = f.read().splitlines()
train_labels = [int(label) for label in train_labels]

train_set = []
with open('data/train_bag_of_words_5.csv') as csvfile:
    d = {}
    reader = csv.reader(csvfile)
    j = 0
    for row in reader:
        for i in range(len(row)):
            d[vocab[i]] = int(row[i])
        train_set.append((d, train_labels[j]))
        j += 1
   
f = open('data/test_classes_0.txt', 'r')
test_labels = f.read().splitlines()
test_labels = [int(label) for label in test_labels]

test_set = []
with open('data/test_bag_of_words_0.csv') as csvfile:
    d = {}
    reader = csv.reader(csvfile)
    j = 0
    for row in reader:
        for i in range(len(row)):
            d[vocab[i]] = int(row[i])
        test_set.append((d, test_labels[j]))
        j += 1

train_labels, train_set, test_labels, test_set = get_final_lists(train_labels, train_set, test_labels, test_set)


classifier = nltk.NaiveBayesClassifier.train(train_set)


tp = 0
tn = 0
fp = 0
fn = 0
right = 0
pred = [classifier.classify(data[0]) for data in test_set]
true = [data[1] for data in test_set]
for i in range(len(test_set)):
    label = classifier.classify(test_set[i][0])
    if label == 1 and test_labels[i] == 1:
        tp += 1
    elif label == 1 and test_labels[i] == 0:
        fp += 1
    elif label == 0 and test_labels[i] == 1:
        fn += 1
    elif label == 0 and test_labels[i] == 0:
        tn += 1
    if label == int(test_labels[i]):
        right += 1

print('accuracy', right / len(test_set))
print('accuracy', (tp + tn) / (tp + tn + fp + fn))
precision = tp / (tp + fp)
print('precision', precision)
recall = tp / (tp + fn)
print('recall', recall)
print("f1", 2 * recall * precision / (recall + precision))
print('pred', pred)
print(precision_recall_fscore_support(true, pred))
