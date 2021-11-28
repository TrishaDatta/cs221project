import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
import time
import csv
from sklearn.feature_selection import SelectKBest, chi2

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

i = 0
with open('train_bag_of_words_5.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        url_to_bow[train_urls[i]] = [int(r) for r in row]
        i += 1

i = 0
with open('test_bag_of_words_0.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        url_to_bow[test_urls[i]] = [int(r) for r in row]
        i += 1

with open('urlToNodeNumber.txt', encoding="utf8") as nodefile:
     lines = nodefile.readlines()
     for line in lines:
          cels = line.strip().split(' , ')
          labels.append(int(cels[2]))
          url = cels[0].lower()
          node_num_to_url[int(cels[1])] = url
          x.append(url_to_bow[cels[0].lower()])
          if url in train_urls:
              train_mask.append(True)
              test_mask.append(False)
          elif url in test_urls:
              train_mask.append(False)
              test_mask.append(True)
          else:
              raise Exception()
            

with open('edges.txt', encoding="utf8") as edgefile:
     lines = edgefile.readlines()
     for line in lines:
          cels = line.strip().split(' , ')
          edge_1.append(int(cels[0]))
          edge_1.append(int(cels[1]))
          edge_2.append(int(cels[1]))
          edge_2.append(int(cels[0]))

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
accuracies [0.6428571428571429, 0.6224489795918368, 0.6326530612244898, 0.6530612244897959, 0.5816326530612245, 0.6020408163265306, 0.7040816326530612, 0.6122448979591837, 0.6122448979591837, 0.7551020408163265, 0.6020408163265306, 0.5816326530612245, 0.5714285714285714, 0.6224489795918368, 0.5918367346938775, 0.673469387755102, 0.7346938775510204, 0.5714285714285714, 0.6428571428571429, 0.6020408163265306, 0.5816326530612245, 0.5816326530612245, 0.6326530612244898, 0.6122448979591837, 0.6428571428571429, 0.5714285714285714, 0.5408163265306123, 0.5918367346938775, 0.5918367346938775, 0.5816326530612245, 0.5918367346938775, 0.5816326530612245, 0.6020408163265306, 0.6938775510204082, 0.6020408163265306, 0.5918367346938775, 0.6326530612244898, 0.6020408163265306, 0.6428571428571429, 0.6836734693877551, 0.6224489795918368, 0.5714285714285714, 0.5408163265306123, 0.6122448979591837, 0.6020408163265306, 0.6020408163265306, 0.6122448979591837, 0.6938775510204082, 0.7551020408163265, 0.7448979591836735, 0.5816326530612245, 0.7040816326530612, 0.6020408163265306, 0.6020408163265306, 0.6224489795918368, 0.6428571428571429, 0.5918367346938775, 0.6020408163265306, 0.6632653061224489, 0.7244897959183674, 0.5612244897959183, 0.5918367346938775, 0.5306122448979592, 0.6836734693877551, 0.5714285714285714, 0.5918367346938775, 0.6224489795918368, 0.6224489795918368, 0.6326530612244898, 0.6122448979591837, 0.6326530612244898, 0.6428571428571429, 0.7551020408163265, 0.6530612244897959, 0.7653061224489796, 0.6020408163265306, 0.5714285714285714, 0.6224489795918368, 0.7448979591836735, 0.6020408163265306, 0.673469387755102, 0.6632653061224489, 0.5408163265306123, 0.5714285714285714, 0.6224489795918368, 0.5612244897959183, 0.6938775510204082, 0.5714285714285714, 0.5918367346938775, 0.6326530612244898, 0.7346938775510204, 0.5714285714285714, 0.5510204081632653, 0.6530612244897959, 0.6020408163265306, 0.5918367346938775, 0.5612244897959183, 0.6020408163265306, 0.5816326530612245, 0.5816326530612245]
precisions [0.6349206349206349, 0.6119402985074627, 0.6, 0.618421052631579, 0.5647058823529412, 0.5764705882352941, 0.9259259259259259, 0.5897435897435898, 0.5875, 0.9666666666666667, 0.5764705882352941, 0.5647058823529412, 0.5581395348837209, 0.5925925925925926, 0.5714285714285714, 0.9166666666666666, 0.9642857142857143, 0.5735294117647058, 0.6049382716049383, 0.5764705882352941, 0.5632183908045977, 0.5662650602409639, 0.5975609756097561, 0.5897435897435898, 0.6133333333333333, 0.5735294117647058, 0.5393258426966292, 0.5789473684210527, 0.5714285714285714, 0.5632183908045977, 0.62, 0.5662650602409639, 0.5764705882352941, 0.9583333333333334, 0.5764705882352941, 0.5697674418604651, 0.6052631578947368, 0.5764705882352941, 0.6133333333333333, 1.0, 0.5925925925925926, 0.5657894736842105, 0.5522388059701493, 0.6346153846153846, 0.5783132530120482, 0.5764705882352941, 0.6166666666666667, 0.9583333333333334, 0.9666666666666667, 0.9354838709677419, 0.582089552238806, 0.96, 0.5764705882352941, 0.5730337078651685, 0.6470588235294118, 0.9047619047619048, 0.575, 0.5730337078651685, 1.0, 0.8378378378378378, 0.5542168674698795, 0.5769230769230769, 1.0, 1.0, 0.5595238095238095, 0.5697674418604651, 0.5925925925925926, 0.5949367088607594, 0.6025641025641025, 0.5875, 0.6025641025641025, 0.6049382716049383, 0.9666666666666667, 0.6125, 1.0, 0.5802469135802469, 0.5609756097560976, 0.6027397260273972, 1.0, 0.5764705882352941, 0.8846153846153846, 1.0, 1.0, 0.5595238095238095, 0.5949367088607594, 0.5517241379310345, 1.0, 0.5581395348837209, 0.5697674418604651, 0.6, 0.9642857142857143, 0.5543478260869565, 1.0, 0.6125, 0.5942028985507246, 0.5697674418604651, 0.5494505494505495, 0.5866666666666667, 0.5632183908045977, 0.6]
recalls [0.7692307692307693, 0.7884615384615384, 0.9230769230769231, 0.9038461538461539, 0.9230769230769231, 0.9423076923076923, 0.4807692307692308, 0.8846153846153846, 0.9038461538461539, 0.5576923076923077, 0.9423076923076923, 0.9230769230769231, 0.9230769230769231, 0.9230769230769231, 0.9230769230769231, 0.4230769230769231, 0.5192307692307693, 0.75, 0.9423076923076923, 0.9423076923076923, 0.9423076923076923, 0.9038461538461539, 0.9423076923076923, 0.8846153846153846, 0.8846153846153846, 0.75, 0.9230769230769231, 0.8461538461538461, 0.9230769230769231, 0.9423076923076923, 0.5961538461538461, 0.9038461538461539, 0.9423076923076923, 0.4423076923076923, 0.9423076923076923, 0.9423076923076923, 0.8846153846153846, 0.9423076923076923, 0.8846153846153846, 0.40384615384615385, 0.9230769230769231, 0.8269230769230769, 0.7115384615384616, 0.6346153846153846, 0.9230769230769231, 0.9423076923076923, 0.7115384615384616, 0.4423076923076923, 0.5576923076923077, 0.5576923076923077, 0.75, 0.46153846153846156, 0.9423076923076923, 0.9807692307692307, 0.6346153846153846, 0.36538461538461536, 0.8846153846153846, 0.9807692307692307, 0.36538461538461536, 0.5961538461538461, 0.8846153846153846, 0.8653846153846154, 0.11538461538461539, 0.40384615384615385, 0.9038461538461539, 0.9423076923076923, 0.9230769230769231, 0.9038461538461539, 0.9038461538461539, 0.9038461538461539, 0.9038461538461539, 0.9423076923076923, 0.5576923076923077, 0.9423076923076923, 0.5576923076923077, 0.9038461538461539, 0.8846153846153846, 0.8461538461538461, 0.5192307692307693, 0.9423076923076923, 0.4423076923076923, 0.36538461538461536, 0.1346153846153846, 0.9038461538461539, 0.9038461538461539, 0.9230769230769231, 0.4230769230769231, 0.9230769230769231, 0.9423076923076923, 0.9230769230769231, 0.5192307692307693, 0.9807692307692307, 0.15384615384615385, 0.9423076923076923, 0.7884615384615384, 0.9423076923076923, 0.9615384615384616, 0.8461538461538461, 0.9423076923076923, 0.6346153846153846]
f1s [0.6956521739130435, 0.6890756302521007, 0.7272727272727274, 0.734375, 0.7007299270072993, 0.7153284671532847, 0.6329113924050633, 0.7076923076923076, 0.7121212121212122, 0.7073170731707317, 0.7153284671532847, 0.7007299270072993, 0.6956521739130436, 0.7218045112781956, 0.7058823529411765, 0.5789473684210527, 0.6749999999999999, 0.65, 0.7368421052631579, 0.7153284671532847, 0.7050359712230214, 0.6962962962962963, 0.7313432835820896, 0.7076923076923076, 0.7244094488188976, 0.65, 0.6808510638297872, 0.6875, 0.7058823529411765, 0.7050359712230214, 0.607843137254902, 0.6962962962962963, 0.7153284671532847, 0.6052631578947368, 0.7153284671532847, 0.7101449275362319, 0.71875, 0.7153284671532847, 0.7244094488188976, 0.5753424657534247, 0.7218045112781956, 0.671875, 0.6218487394957983, 0.6346153846153846, 0.7111111111111112, 0.7153284671532847, 0.6607142857142857, 0.6052631578947368, 0.7073170731707317, 0.6987951807228916, 0.6554621848739495, 0.6233766233766234, 0.7153284671532847, 0.7234042553191489, 0.6407766990291263, 0.5205479452054794, 0.696969696969697, 0.7234042553191489, 0.5352112676056338, 0.6966292134831461, 0.6814814814814815, 0.6923076923076923, 0.20689655172413793, 0.5753424657534247, 0.6911764705882352, 0.7101449275362319, 0.7218045112781956, 0.7175572519083969, 0.7230769230769231, 0.7121212121212122, 0.7230769230769231, 0.7368421052631579, 0.7073170731707317, 0.7424242424242424, 0.7160493827160493, 0.7067669172932332, 0.6865671641791045, 0.7040000000000001, 0.6835443037974684, 0.7153284671532847, 0.5897435897435898, 0.5352112676056338, 0.23728813559322035, 0.6911764705882352, 0.7175572519083969, 0.6906474820143885, 0.5945945945945945, 0.6956521739130436, 0.7101449275362319, 0.7272727272727274, 0.6749999999999999, 0.7083333333333333, 0.2666666666666667, 0.7424242424242424, 0.6776859504132232, 0.7101449275362319, 0.6993006993006995, 0.6929133858267718, 0.7050359712230214, 0.616822429906542]

'''