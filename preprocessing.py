#%%
from scipy.io import mmread
import tarfile

#%%

# Load adjacency matrix of Les miserables dataset
A = mmread('data/lesmis.mtx').todense()


adj = {}
txt = ''
for i, j in enumerate(A):
    temp_list = A[i].tolist()[0]
    adj[i] = [k for k in range(len(temp_list)) if temp_list[k] != 0]
    for k in adj[i]:
        txt += f'{i}-{k}\n'

text_file = open("data/lesmis_unweighted.txt", "w")
n = text_file.write(txt)
text_file.close()
#%%

adj = {}
txt = ''
for i, j in enumerate(A):
    temp_list = A[i].tolist()[0]
    adj[i] = [k for k in range(len(temp_list)) if temp_list[k] != 0]
    for k in adj[i]:
        txt += f'{i}-{k}-{temp_list[k]}\n'

text_file = open("data/lesmis_weighted.txt", "w")
n = text_file.write(txt)
text_file.close()

#%%

# Facebook dataset

tar = tarfile.open("data/facebook.tar.gz", "r:gz")
for member in tar.getmembers():
     f = tar.extractfile(member)
     if f is not None:
        content = f.read()
        print(member)

#%%

content = content.decode('utf-8').replace(' ', '-')

text_file = open("data/facebook.txt", "w")
n = text_file.write(content)
text_file.close()

#%%

# Star wars dataset

import json

f = open('data/raw data/starwars.json')

data = json.load(f)
txt = ''

for i in data['links']:
    source = i['source']
    target = i['target']
    txt += f'{source}-{target}\n'

text_file = open("data/starwars.txt", "w")
n = text_file.write(txt)
text_file.close()

#%%

from bz2 import BZ2File as bzopen

file = 'data/raw data/download.tsv.sociopatterns-infectious.tar.bz2'

with bzopen(file, "r") as bzfin:
    """ Handle lines here """
    txt = ''
    for line in bzfin:
        txt += f'{line.rstrip()}\n'

text_file = open("data/galleryprox.txt", "w")
n = text_file.write(txt)
text_file.close()

#%%


file = 'data/raw data/galleryprox.txt'
txt = ''

for line in open(file):
    L = line.strip().split(' ')
    txt += f'{L[0][2:]}-{L[1]}\n'

text_file = open("data/Gallery Proximity.txt", "w")
n = text_file.write(txt)
text_file.close()
#%%

import pandas as pd

file = 'data/raw data/TrumpWorld Data — Public.xlsx'

df = pd.read_excel(file)

unique_vals = list(set(df['Entity A'].unique().tolist() + df['Entity B'].unique().tolist()))
dict_labels = {}

for i, val in enumerate(unique_vals):
    dict_labels[val] = i

df['edges'] = df.apply(lambda row: str(dict_labels[row['Entity A']])+'-'+str(dict_labels[row['Entity B']]), axis=1)

df['edges'].to_csv('data/TrumpWorld.txt', header=None, index=None, sep='\n')

#%%


file = 'data/raw data/mol_yeast_spliceosome_2017.txt'
txt = ''

for i, line in enumerate(open(file)):
    L = line.strip().split('\t')
    tmp = [k for k in range(len(L)) if float(L[k]) != 0]
    for k in tmp:
        txt += f'{i}-{k}\n'

text_file = open("data/Yeast spliceosome.txt", "w")
n = text_file.write(txt)
text_file.close()
#%%

import gzip
import os

for i, file in enumerate(os.listdir('data/raw data/Oregon/')):
    f = os.path.join('data/raw data/Oregon/', file)
    # checking if it is a file
    if os.path.isfile(f):
        txt = ''

        with gzip.open(f,'rt') as fnew:
            for line in fnew:
                if line[0].isdigit():
                    L = line.strip().split('\t')
                    txt += f'{L[0]}-{L[1]}\n'

        text_file = open(f"data/Oregon_{i}.txt", "w")
        n = text_file.write(txt)
        text_file.close()
                

#%%

df = pd.read_excel('data/raw data/LabanderiaDunne2014DryadData.xls')

df.head()

#%%