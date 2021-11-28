import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
import time
import csv
from sklearn.feature_selection import SelectKBest, chi2
import numpy as np

class GCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(len(data.x[0]), 16)
        self.conv2 = GCNConv(16, 2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index)

        return F.log_softmax(x, dim=1)


t0 = time.time()

edge_1 = []
edge_2 = []
labels = []
train_mask = []
node_num_to_url = {}
train_fake_urls = None
train_real_urls = None
test_fake_urls = None
test_real_urls = None
url_to_bow = {}
x = []

with open('train_fake_urls', encoding="utf8") as datafile:
     train_fake_urls = [line.strip().lower() for line in datafile.readlines()]

with open('train_real_urls', encoding="utf8") as datafile:
     train_real_urls = [line.strip().lower() for line in datafile.readlines()]

with open('test_fake_urls', encoding="utf8") as datafile:
     test_fake_urls = [line.strip().lower() for line in datafile.readlines()]

with open('test_real_urls', encoding="utf8") as datafile:
     test_real_urls = [line.strip().lower() for line in datafile.readlines()]

train_urls = train_fake_urls + train_real_urls
test_urls = test_fake_urls + test_real_urls

train_mask = []
test_mask = []

urlToIndex = {}

i = 0
j = 0
with open('train_bag_of_words_5.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        url_to_bow[train_urls[i]] = [int(r) for r in row]
        urlToIndex[train_urls[i]] = j
        i += 1
        j += 1

i = 0
with open('test_bag_of_words_0.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        url_to_bow[test_urls[i]] = [int(r) for r in row]
        urlToIndex[test_urls[i]] = j
        i += 1
        j += 1


nodeNumberToIndex = {}

with open('urlToNodeNumber.txt', encoding="utf8") as nodefile:
     lines = nodefile.readlines()
     for line in lines:
          cels = line.strip().split(' , ')
          labels.append(int(cels[2]))
          url = cels[0].lower()
          nodeNumber = int(cels[1])
          node_num_to_url[nodeNumber] = url
          nodeNumberToIndex[nodeNumber] = urlToIndex[url]
          x.append(url_to_bow[cels[0].lower()])
          if url in train_urls:
              train_mask.append(True)
              test_mask.append(False)
          elif url in test_urls:
              train_mask.append(False)
              test_mask.append(True)
          else:
              raise Exception()
print(j)

tfidfs = np.load('tfidf.npy')

for i in range(len(nodeNumberToIndex)):
     for j in range(len(nodeNumberToIndex)):
          index1 = nodeNumberToIndex[i]
          index2 = nodeNumberToIndex[j]
          if tfidfs[index1][index2] > 0.001:
               edge_1.append(i)
               edge_1.append(j)
               edge_2.append(j)
               edge_2.append(i)

'''$ py tfidf_pyg.py
356950
356950
459
5812
459
accuracy 0.5306122448979592
accuracy 0.5306122448979592
precision 0.5306122448979592
recall 1.0
f1 0.6933333333333334
took 44.65538811683655 seconds'''


'''
839
356950
356950
459
5812
459
accuracy 0.5612244897959183
accuracy 0.5612244897959183
precision 0.6451612903225806
recall 0.38461538461538464
f1 0.4819277108433735
took 40.75327229499817 seconds

'''


print(len(edge_1))
print(len(edge_2))
print(len(x))
print(len(x[0]))
print(len(labels))

x_new = SelectKBest(chi2, k=4000).fit_transform(x, labels)




edge_index = torch.tensor([edge_1,
                           edge_2], dtype=torch.long)


x_tensor = torch.tensor(x_new, dtype=torch.float)
y_tensor = torch.tensor(labels, dtype=torch.long)


data = Data(x = x_tensor, y = y_tensor, edge_index=edge_index)

data.train_mask = torch.tensor(train_mask, dtype=torch.bool)
data.test_mask = torch.tensor(test_mask, dtype=torch.bool)

accuracies = []
precisions = []
recalls = []
f1s = []

for i in range(100):
     print('trial', i)
     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
     model = GCN().to(device)
     data = data.to(device)
     optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)


     model.train()


     for epoch in range(50):
         optimizer.zero_grad()
         out = model(data)
         loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
         loss.backward()
         optimizer.step()


     model.eval()
     pred_tensor = model(data).argmax(dim=1)

     preds = pred_tensor[data.test_mask].tolist()
     reals = data.y[data.test_mask].tolist()

     tp = 0
     tn = 0
     fp = 0
     fn = 0
     right = 0
     for i in range(len(preds)):
         pred = preds[i]
         real = reals[i]
         
         if pred == 1 and real == 1:
             tp += 1
         elif pred == 1 and real == 0:
             fp += 1
         elif pred == 0 and real == 1:
             fn += 1
         elif pred == 0 and real == 0:
             tn += 1
         if pred == real:
             right += 1

     try:
          accuracy = (tp + tn) / (tp + tn + fp + fn)
          accuracies.append(accuracy)
          print('accuracy', accuracy)

          precision = tp / (tp + fp)
          precisions.append(precision)
          print('precision', precision)
          
          recall = tp / (tp + fn)
          recalls.append(recall)
          print('recall', recall)

          f1 = 2 * recall * precision / (recall + precision)
          f1s.append(f1)
          print("f1", f1)
     except:
          yyy = 1


print('accuracies', accuracies)
print('precisions', precisions)
print('recalls', recalls)
print('f1s', f1s) 

t1 = time.time()

total = t1-t0
print("took " + str(total) + " seconds")




'''
accuracies [0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.42857142857142855, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5612244897959183, 0.46938775510204084, 0.5102040816326531, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.5306122448979592, 0.5306122448979592, 0.46938775510204084, 0.5510204081632653, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.5408163265306123, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.4489795918367347, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084, 0.5306122448979592, 0.46938775510204084, 0.46938775510204084, 0.46938775510204084]
precisions [0.5306122448979592, 0.5306122448979592, 0.16666666666666666, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5494505494505495, 0.5526315789473685, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5306122448979592, 0.5454545454545454, 0.5306122448979592, 0.5306122448979592, 0.5368421052631579, 0.45454545454545453, 0.5306122448979592, 0.5306122448979592]
recalls [1.0, 1.0, 0.019230769230769232, 1.0, 1.0, 1.0, 0.9615384615384616, 0.40384615384615385, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9230769230769231, 1.0, 1.0, 0.9807692307692307, 0.19230769230769232, 1.0, 1.0]
f1s [0.6933333333333334, 0.6933333333333334, 0.034482758620689655, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6993006993006995, 0.46666666666666673, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6933333333333334, 0.6857142857142856, 0.6933333333333334, 0.6933333333333334, 0.6938775510204082, 0.27027027027027023, 0.6933333333333334, 0.6933333333333334]
'''
