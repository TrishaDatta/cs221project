import time
import csv

t0 = time.time()


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
all_urls = train_urls + test_urls
fake_urls = train_fake_urls + test_fake_urls
real_urls = train_real_urls + test_real_urls

missing = []

node_urls = set()

with open('urlToNodeNumber.txt', encoding="utf8") as nodefile:
     lines = nodefile.readlines()
     for line in lines:
          cels = line.strip().split(' , ')
          url = cels[0].lower()
          node_urls.add(url)

fake = 0
real = 0

for url in all_urls:
     if url not in node_urls:
          if url in fake_urls:
               fake += 1
          if url in real_urls:
               real += 1

print('fake', fake)
print('real', real) 
          

              

