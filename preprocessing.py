#%%
from scipy.io import mmread

# Load adjacency matrix of Les miserables dataset
A = mmread('lesmis/lesmis.mtx').todense()

adj = {}
txt = ''
for i, j in enumerate(A):
    temp_list = A[i].tolist()[0]
    adj[i] = [k for k in range(len(temp_list)) if temp_list[k] != 0]
    for k in adj[i]:
        txt += f'{i}-{k}\n'

text_file = open("lesmis/lesmis.txt", "w")
n = text_file.write(txt)
text_file.close()
#%%