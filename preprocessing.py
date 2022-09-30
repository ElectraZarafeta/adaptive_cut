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

