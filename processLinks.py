#https://towardsdatascience.com/pyvis-visualize-interactive-network-graphs-in-python-77e059791f01
import csv
import sys
from collections import defaultdict
from pyvis.network import Network
import random


def process(string):
     x = string.strip()
     x = x.replace('%3A', ':')
     x = x.replace('%2F', '/')
     if x.startswith('https://web.archive.org'):
          x = x[23:]
          i = x.find('http')
          x = x[i:]
     if x.startswith('http://'):
          x = x[7:]
          x = x.split('/', 1)[0]
          return x
     if x.startswith('https://'):
          x = x[8:]
          x = x.split('/', 1)[0]
          return x
     if 'http://' in x:
          i = x.find('https://')
          x = x[i + 7:]
          x = x.split('/', 1)[0]
          return x
     if 'https://' in x:
          i = x.find('https://')
          x = x[i + 8:]
          x = x.split('/', 1)[0]
          return x
     return None



def getColorIndex(string, fake_urls, real_urls):
     if string in fake_urls:
          return 1
     elif string in real_urls:
          return 0
     return 2

net = Network()

nodes = defaultdict(int)
edges = defaultdict(set)

colors = ['green', 'red', 'gray']

fake_urls = ''
with open('all_fake_urls') as train_fake_urls_file:
     fake_urls = train_fake_urls_file.read().lower()

real_urls = ''
with open('all_real_urls') as train_real_urls_file:
     real_urls = train_real_urls_file.read().lower()


counts = defaultdict(set)
url_to_domain = {}

files = ['linkFile.txt', 'newLinkFile.txt']

for f in files:
     with open(f, encoding="utf8") as linkfile:
          lines = linkfile.readlines()
          for line in lines:
               link = line.strip().split(' , ', 1)
               if len(link) != 2:
                    continue

               first_url = link[0].lower()

               second_domain = process(link[1].lower())

               firstColorIndex = getColorIndex(first_url, fake_urls, real_urls)
               #secondColorIndex = getColorIndex(link[1], fake_urls, real_urls)

               if first_url != None:
                    nodes[first_url] = firstColorIndex
               if second_domain != None:
                    # nodes[second] = secondColorIndex
                    if firstColorIndex != 2:
                         counts[second_domain].add(first_url)
               '''if first != None and second != None:
                    if first != second:
                         edges[first].add(second)'''


#f = open("urlToNodeNumber.txt", "w")
addedNodes = set()
nodeToNum = {}
c = 0
for node in nodes:
     if random.random() < 0.2:
          net.add_node(c, node, color=colors[nodes[node]])
          addedNodes.add(node)
     #f.write(node + ' , ' + str(c) + ' , ' + str(nodes[node]) + '\n')
     nodeToNum[node] = c
     c += 1

#f.close()
     

#f = open("edges.txt", "w")
for count in counts:
     if len(counts[count]) > 1:
          edge_nodes = list(counts[count])
          for i in range(len(edge_nodes)):
               for j in range(i + 1, len(edge_nodes)):
                    if edge_nodes[i] in addedNodes and edge_nodes[j] in addedNodes:
                         net.add_edge(nodeToNum[edge_nodes[i]], nodeToNum[edge_nodes[j]])

                    #net.add_edge(nodes[edge_nodes[i]], nodes[edge_nodes[j]])
                    #f.write(str(nodes[edge_nodes[i]]) + ' , ' + str(nodes[edge_nodes[j]]) + '\n')

#f.close()'''
                  

'''for node in edges:
     for edge in edges[node]:
          net.add_edge(nodes[node], nodes[edge])'''

print('length of nodes', len(nodes))


net.show('edge_artificial.html')

