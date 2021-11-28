# Import packages for data cleaning
import numpy as np
import pandas as pd
import re # For finding specific strings in the text
# Import packages for data visualization
import networkx as nx
from urllib.parse import urlparse
from networkx.algorithms import community
import socket
import socket
import pycountry
import urllib
import whois 
import sys
## Load in datasets for performing analysis 
import pandas as pd
#reader = geoip2.database.Reader('/mnt/projects/GeoLite2-Country_20201124/GeoLite2-Country.mmdb')
from publicsuffix2 import PublicSuffixList
psl = PublicSuffixList()
#asndb = pyasn.py
import json
#import pysasn
import io


import socket
import pyasn
asndb = pyasn.pyasn('ipasn_20201203.dat')
domain_to_ips = dict()
def getDomainIPS(domains):
  for domain in domains:
    try: 
      domain_to_ips[domain] = []
      domain_to_ips[domain].extend([socket.gethostbyname(domain)])
    except Exception as e:
      try:
        domain_to_ips[domain].extend([socket.gethostbyname('www.'+domain)])
      except Exception as e:
        print(e)
  return domain_to_ips



def getDomainASInfo(domain_to_ips):
  as_codes = dict()
  as_codes_domains = dict()
  domain_to_as = dict()
  index =0
  for domain in list(domain_to_ips.keys()):
    if domain is not None:
      current_set = set()
      if domain in domain_to_ips:
        for ip in domain_to_ips[domain]:
          try:
            ascode,bgp_prefix = asndb.lookup(ip)
            current_set.add(ascode)
          except:
            print(ip)
        domain_to_as[domain] = list(current_set)
        for ascode in current_set:
          if ascode not in as_codes:
            as_codes[ascode] = 0
          as_codes[ascode] += 1
  return domain_to_as,as_codes_domains,as_codes


import time
def get_whois_features(domains):
    registrars = []
    organizations = []
    countries = []
    time_since_registration = []
    time_since_update = []
    time_to_expiration = []
    domain_life_span = []
    name_servers = []
    names = []
    full_data = []
    for domain in domains:
      time.sleep(3)
      try:
        print(domain)
        whois_info = whois.whois(domain)
        if 'registrar' in whois_info:
            registrars.append(whois_info['registrar'])
        else:
            registrars.append('NA')
        if 'org' in whois_info:
            organizations.append(whois_info['org'])
        else:
            organizations.append('NA')  
        if 'country' in whois_info:
            countries.append(whois_info['country'])
        else:
            countries.append('NA')
        if 'name_servers' in whois_info:
          name_servers.append(whois_info['name_servers'])
        else:
          name_servers.append('NA')
        if 'name' in whois_info:
          names.append(whois_info['name'])
        else:
          names.append('NA')
        if 'creation_date' in whois_info:
            start_times = whois_info['creation_date']
        min_start_time = float(RIGHT_NOW)
        if isinstance(start_times, list): 
            try:
                for start_time in start_times:
                    if float(start_time.timestamp()) < float(min_start_time):
                        min_start_time = start_time.timestamp()
            except Exception as e:
                print(e)
            time_since_registration.append(RIGHT_NOW -min_start_time)
        elif 'creation_date' in whois_info:
            if whois_info['creation_date'] is not None:
                try:
                    time_since_registration.append(RIGHT_NOW- whois_info['creation_date'].timestamp())
                except:
                    if 'before' in whois_info['creation_date']:
                        time_since_registration.append(839355887)
            else:
                time_since_registration.append(float("nan"))     
        else:
            time_since_registration.append(float("nan"))


        if 'updated_date' in whois_info:
            update_times = whois_info['updated_date']
        max_update_time = 0
        if isinstance(update_times, list): 
            for update_time in update_times:
                try:
                    if float(update_time.timestamp())> float(max_update_time):
                        max_update_time = update_time.timestamp()
                except Exception as e:
                    print(e)
            time_since_update.append(RIGHT_NOW- max_update_time)
        elif 'updated_date' in whois_info:
            if whois_info['updated_date'] is not None:
                time_since_update.append(RIGHT_NOW- whois_info['updated_date'].timestamp() )
            else:
                time_since_update.append(float("nan"))  
        else:
            time_since_update.append(float("nan"))


        if 'expiration_date' in whois_info:
            expiration_times = whois_info['expiration_date']
        max_expiration_time = 0
        if isinstance(expiration_times, list): 
            try:
                for expir_time in expiration_times:
                    if float(expir_time.timestamp()) > float(max_expiration_time):
                        max_expiration_time = expir_time.timestamp()
            except Exception as e:
                print(e)
            time_to_expiration.append(max_expiration_time- RIGHT_NOW)
        elif 'expiration_date' in whois_info:
            if whois_info['expiration_date'] is not None:
                time_to_expiration.append(whois_info['expiration_date'].timestamp()- RIGHT_NOW)
            else:
                time_to_expiration.append(float("nan"))
        else:
            time_to_expiration.append(float("nan"))
        if max_expiration_time != 0 and min_start_time !=RIGHT_NOW:
            domain_life_span.append(max_expiration_time-min_start_time)
        else:
            domain_life_span.append(float("nan"))
      except:
        registrars.append('')
        organizations.append('')
        countries.append('')
        time_since_registration.append('')
        time_since_update.append('')
        time_to_expiration.append('')
        domain_life_span.append('')
        name_servers.append('')
        names.append('')
    full_data.append(registrars)
    full_data.append(organizations)
    full_data.append(countries)
    full_data.append(time_since_registration)
    full_data.append(time_since_update)
    full_data.append(time_to_expiration)
    full_data.append(domain_life_span)
    full_data.append(names)
    full_data.append(name_servers)
    
    return full_data, registrars,organizations, countries,time_since_registration, time_since_update,time_to_expiration,domain_life_span,names,name_servers



def get_whois_features_nameservers(name_servers):
  countries = dict()
  ips = getDomainIPS(name_servers)
  ases = getDomainASInfo(ips)
  for server in name_servers:
    try:
        whois_info = whois.whois(server)
        if 'country' in whois_info:
            countries[server]= whois_info['country']
        else:
            countries[server]= 'NA'
    except:
        countries[server]= 'NA'
  all_info = [ases, countries]
  return all_info


def get_domain_resolves(domains, domain_to_ips):
    domain_resolves = []
    for domain in domains:
        if len(domain_to_ips[domain]) > 0:
            domain_resolves.append(1)
        else:
            domain_resolves.append(0)
    return domain_resolves


def get_domain_as(domains, training_set_domains_ases):
    domain_ases = []
    for domain in domains:
        if len(training_set_domains_ases[domain]) > 0:
            domain_ases.append(training_set_domains_ases[domain][0])
        else:
            domain_ases.append('NA')
    return domain_ases


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)



def get_domain_keyword_features(domains):
    news_words = ['times','herald','tribune','chronicle','post','today',
                  'press','observer','sun','paper','media','stand','journal',
                  'independent','globe','mail','inquirer','courant', 'telegraph',
                  'dispatch', 'express', 'daily','dispatch','sentinel','gazette',
                  'standard','telegram']
    contain_news_words = []
    for domain in domains:
        for word in news_words:
            contains_news_word = False
            if word in domain:
                contains_news_word = True
                break
        if contains_news_word:
            contain_news_words.append(1)
        else:
            contain_news_words.append(0)
    return contain_news_words             


def get_domain_lengths(domains):
    domain_lengths = []
    for domain in domains:
        domain_lengths.append(len(domain))
    return domain_lengths 


def get_contains_news(domains):
    contains_news = []
    for domain in domains:
        if 'news' in domain:
            contains_news.append(1)
        else:
            contains_news.append(0)
    return contains_news


def get_contains_hypen(domains):
    contains_hypen = []
    for domain in domains:
        if '-' in domain:
            contains_hypen.append(1)
        else:
            contains_hypen.append(0)
    return contains_hypen

def get_contains_number(domains):
    contains_number = []
    for domain in domains:
        if hasNumbers(domain):
            contains_number.append(1)
        else:
            contains_number.append(0)
    return contains_number

def get_tld_novel(domains):
    normal_tlds = ['com','net','org','edu']
    contains_tld_novel = []
    for domain in domains:
        tld = domain.split('.')[-1]
        if tld not in normal_tlds:
            contains_tld_novel.append(1)
        else:
            contains_tld_novel.append(0)
    return contains_tld_novel


def get_domains(urls):
  domains = []
  for url in urls:
    node1_domain = urlparse(url).hostname
    node1_domain = node1_domain.strip('\r\n')
    node1_domain = node1_domain.replace("www.","")
    domains.append(node1_domain)
  return domains

def get_whois_privacy(names):
  privacy = []
  for name in names:
    name = str(name)
    if name == name and name is not None:
      if 'priv' in name.lower() or 'proxy' in name.lower() or 'protect' in name.lower() or 'masking' in name.lower():
        privacy.append(1)
      else:
        privacy.append(0)
    else:
      privacy.append(1)
  return privacy


def get_sld_name(name_severs):
  slds = []
  for server in name_severs:
    if server is not None:
      if isinstance(server, list):
        try:
          server = server[0].split(' ')[0]
          slds.append(server.split('.')[-2].lower())
        except:
          slds.append('NA')
      else:
        server = server.split(' ')[0]
        try:
          slds.append(server.split('.')[-2].lower())
        except:
          slds.append('NA')
    else:
      slds.append('NA')
  return slds


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

with open('urlToNodeNumber.txt', encoding="utf8") as nodefile:
     lines = nodefile.readlines()
     for line in lines:
          cels = line.strip().split(' , ')
          url = cels[0].lower()
          processed_url = process(url)
          print(processed_url)

full_data,registrars,organizations, \
                                    countries,time_since_registration, \
                                    time_since_update,time_to_expiration, \
                                    domain_life_span,names,name_server \
                                    = get_whois_features(['nationalreport.net'])

print('regs',registrars)
print('orgs',organizations)
print('countries',countries)
print('time',time_since_registration)
print('time since', time_since_update)
print('time to exp',time_to_expiration)
print('dom life span',domain_life_span)
print('names',names)
print('name serv',name_server)
