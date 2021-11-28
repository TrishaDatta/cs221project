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
from nltk.util import ngrams

chars = ['{','}','#','%','&','\(','\)','\[','\]','<','>',',', '!', '.', ';', 
'?', '*', '\\', '\/', '~', '_','|','=','+','^',':','\"','\'','@','-']

def stem(word):
   regexp = r'^(.*?)(ing|ly|ed|ious|ies|ive|es|s|ment)?$'
   stem, suffix = re.findall(regexp, word)[0]
   return stem

def unique(a):
   """ return the list with duplicate elements removed """
   return list(set(a))

def intersect(a, b):
   """ return the intersection of two lists """
   return list(set(a) & set(b))

def union(a, b):
   """ return the union of two lists """
   return list(set(a) | set(b))

def get_files(mypath):
   return [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

def get_dirs(mypath):
   return [ f for f in listdir(mypath) if isdir(join(mypath,f)) ]

# Reading a bag of words file back into python. The number and order
# of sentences should be the same as in the *samples_class* file.
def read_bagofwords_dat(myfile):
  bagofwords = numpy.genfromtxt('myfile.csv',delimiter=',')
  return bagofwords

def tokenize_corpus():

  porter = nltk.PorterStemmer() # also lancaster stemmer
  wnl = nltk.WordNetLemmatizer()
  stopWords = stopwords.words("english")
  classes = []
  samples = []
  docs = []
  
  fake_folder_names = glob('/mnt/misinformation-real-time/FakeNewsNet/code/fakenewsnet_dataset/politifact/fake/*/')
  real_folder_names = glob('/mnt/misinformation-real-time/FakeNewsNet/code/fakenewsnet_dataset/politifact/real/*/')

  fake = []
  real = []

  random.seed(10)
  random.shuffle(fake_folder_names)
  random.shuffle(real_folder_names)

  fake = fake_folder_names[:int(0.8 * len(fake_folder_names))]
  real = real_folder_names[:int(0.8 * len(real_folder_names))]
  

  final_folder_names = fake + real
  for folder_name in final_folder_names:
    files = glob(folder_name +  '*json')
    if len(files) == 0:
       continue
    file = files[0]
    line = ''
    with open(file) as jsonfile:
       try:
         data = json.load(jsonfile)
         line = data['text']
       except:
          x = 9
    if line == '':
       continue

    if 'politifact/fake' in folder_name:
       classes.append("1")
    else:
       classes.append("0")
    raw = re.sub(r'[^a-zA-Z0-9\s]', ' ', line)
    raw = ' '.join(raw.rsplit())
    # remove noisy characters; tokenize
    raw = re.sub('[%s]' % ''.join(chars), ' ', raw)
    tokens = word_tokenize(raw)
    tokens = [w.lower() for w in tokens]
    tokens = [w for w in tokens if w not in stopWords]
    tokens = [wnl.lemmatize(t) for t in tokens]
    tokens = [porter.stem(t) for t in tokens]
    output = list(ngrams(tokens, 3))
    output = [' '.join(o) for o in output]

    if 'presid barack obama' in output:
         print(folder_name)
    


def main(argv):
  
  start_time = time.time()

  tokenize_corpus()


  # Runtime
  print('Runtime:', str(time.time() - start_time))

if __name__ == "__main__":
  main(sys.argv[1:])

 
