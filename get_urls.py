import sys
import csv
import json
from glob import glob
import random
import re


def get_urls(train, getRealSet):  
  fake_folder_names = glob('/mnt/misinformation-real-time/FakeNewsNet/code/fakenewsnet_dataset/politifact/fake/*/')
  real_folder_names = glob('/mnt/misinformation-real-time/FakeNewsNet/code/fakenewsnet_dataset/politifact/real/*/')

  fake = []
  real = []

  random.seed(10)
  random.shuffle(fake_folder_names)
  random.shuffle(real_folder_names)

  if train == True:
    words = {}
    fake = fake_folder_names[:int(0.8 * len(fake_folder_names))]
    real = real_folder_names[:int(0.8 * len(real_folder_names))]
  else:
    fake = fake_folder_names[int(0.8 * len(fake_folder_names)):]
    real = real_folder_names[int(0.8 * len(real_folder_names)):]

  final_folder_names = real if getRealSet else fake
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
          continue
    if line == '':
       continue
    line = data['url']
    if line.startswith('www'):
         line = 'http://' + line
    elif not line.startswith('http'):
         line = 'https://www.' + line
    print(line)


def main(args):
  get_urls(args[0].lower()[0] == 't', args[1].lower()[0] == 'r')
  

if __name__ == "__main__":
  main(sys.argv[1:])

 
