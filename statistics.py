#%%
import mlflow
import pandas as pd
import plotly.express as px

df = pd.DataFrame()

for i in range(8):

    experiment_id = f'{i}'

    runs = mlflow.search_runs(experiment_ids=experiment_id)
    
    df = df.append(runs)

#%%

df = df[['run_id', 'experiment_id', 'metrics.Partition density', 'params.Threshold', 'params.Method']]

#%%

df_pivot = df.pivot(index='experiment_id', columns='params.Method', values='metrics.Partition density')
df_pivot
#%%

df_pivot['Greedy bottom - LC'] = df_pivot['Greedy algorithm bottom'] - df_pivot['Link Clustering']
df_pivot['Greedy up - LC'] = df_pivot['Greedy algorithm up'] - df_pivot['Link Clustering']
df_pivot['Tuning - LC'] = df_pivot['Turing dendrogram cut'] - df_pivot['Link Clustering']  # fix to Tuning
df_pivot
#%%

import plotly.figure_factory as ff


hist_data = [df_pivot['Greedy bottom - LC'].to_numpy(), df_pivot['Greedy up - LC'].to_numpy(), df_pivot['Tuning - LC'].to_numpy()]
group_labels = ['Greedy algorithm bottom', 'Greedy algorithm up', 'Turing dendrogram cut'] # name of the dataset

fig = ff.create_distplot(hist_data, group_labels, bin_size=.1)
fig.show()

#%%

hist_data = [df_pivot['Greedy bottom - LC'].to_numpy()]
group_labels = ['Greedy algorithm bottom'] # name of the dataset

fig = ff.create_distplot(hist_data, group_labels, bin_size=.1)
fig.show()
#%%

hist_data = [df_pivot['Greedy up - LC'].to_numpy()]
group_labels = ['Greedy algorithm up'] # name of the dataset

fig = ff.create_distplot(hist_data, group_labels, bin_size=.05)
fig.show()
# %%

hist_data = [df_pivot['Tuning - LC'].to_numpy()]
group_labels = ['Tuning dendrogram cut'] # name of the dataset

fig = ff.create_distplot(hist_data, group_labels, bin_size=.05)
fig.show()

#%%
