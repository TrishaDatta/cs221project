import nltk, re, pprint
from nltk import word_tokenize
from nltk.corpus import stopwords
from os import listdir
from os.path import isfile, isdir, join
import numpy
import re
import sys
import getopt
import codecs
import time
import os
import csv
import json
from glob import glob
import random
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

chars = ['{','}','#','%','&','\(','\)','\[','\]','<','>',',', '!', '.', ';', 
'?', '*', '\\', '\/', '~', '_','|','=','+','^',':','\"','\'','@','-']

def stem(word):
   regexp = r'^(.*?)(ing|ly|ed|ious|ies|ive|es|s|ment)?$'
   stem, suffix = re.findall(regexp, word)[0]
   return stem



def tokenize_corpus():
  porter = nltk.PorterStemmer() # also lancaster stemmer
  wnl = nltk.WordNetLemmatizer()
  stopWords = stopwords.words("english")
  docs = []
  
  fake_folder_names = glob('/mnt/misinformation-real-time/FakeNewsNet/code/fakenewsnet_dataset/politifact/fake/*/')
  real_folder_names = glob('/mnt/misinformation-real-time/FakeNewsNet/code/fakenewsnet_dataset/politifact/real/*/')

  random.seed(10)
  random.shuffle(fake_folder_names)
  random.shuffle(real_folder_names)

  #train_urls then test_urls

  final_folder_names = fake_folder_names[:int(0.8 * len(fake_folder_names))]
  final_folder_names += real_folder_names[:int(0.8 * len(real_folder_names))]
  final_folder_names += fake_folder_names[int(0.8 * len(fake_folder_names)):]
  final_folder_names += real_folder_names[int(0.8 * len(real_folder_names)):]

  for folder_name in final_folder_names:
    files = glob(folder_name +  '*json')
    if len(files) == 0:
       print('no json file', folder_name)
       continue
    file = files[0]
    line = ''
    with open(file) as jsonfile:
       try:
         data = json.load(jsonfile)
         line = data['text']
       except:
          print('json read error', folder_name)
    if line == '':
       continue

    raw = re.sub(r'[^a-zA-Z0-9\s]', ' ', line)
    raw = ' '.join(raw.rsplit())
    # remove noisy characters; tokenize
    raw = re.sub('[%s]' % ''.join(chars), ' ', raw)
    tokens = word_tokenize(raw)
    tokens = [w.lower() for w in tokens]
    tokens = [w for w in tokens if w not in stopWords]
    tokens = [wnl.lemmatize(t) for t in tokens]
    tokens = [porter.stem(t) for t in tokens]

    processed_line = ' '.join(tokens)     
    docs.append(processed_line)

  return docs


def main(argv):
  
  start_time = time.time()

  documents = tokenize_corpus()

  tfidf = TfidfVectorizer().fit_transform(documents)
  # no need to normalize, since Vectorizer will return normalized tf-idf
  pairwise_similarity = tfidf * tfidf.T
  a = pairwise_similarity.toarray()
  np.save('tfidf.npy', a)
  print(a)


  # Runtime
  print('Runtime:', str(time.time() - start_time))

if __name__ == "__main__":
  main(sys.argv[1:])

 
