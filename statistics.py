#%%
import mlflow
import pandas as pd
import plotly.express as px
import seaborn as sns
import functools as ft
import matplotlib.pyplot as plt
import numpy as np

def min_max_scaling(series):
    return (series - series.min()) / (series.max() - series.min())

df = pd.DataFrame()

exper_lst = [135, 131, 130, 129, 126, 122, 121, 119, 118, 116, 113, 112, 111, 110, 109, 108, 107, 103, 102, 101, 73, 72, 70, 69, 68, 65, 62, 59, 10, 9, 0]

for i in range(136):

    if i in exper_lst:
        experiment_id = f'{i}'

        runs = mlflow.search_runs(experiment_ids=experiment_id)
        
        df = df.append(runs)

df = df[df.status == 'FINISHED']

#%%

df_tmp = df[['experiment_id', 'metrics.Partition density', 'params.Method']]
df_bal = df[['experiment_id', 'metrics.Avg- Max entropy sub Real entropy']].dropna().rename(columns={'metrics.Avg- Max entropy sub Real entropy': 'Balanceness'})
df_size = df[['experiment_id', 'metrics.Network size']].dropna().rename(columns={'metrics.Network size': 'Network size'})

df_best = df_tmp.groupby('experiment_id')['metrics.Partition density'].max().reset_index()

df_tmp2 = df_bal.merge(df_best, on='experiment_id').merge(df_size, on='experiment_id')

sns.scatterplot(x="Balanceness", y="metrics.Partition density", data=df_tmp2)
plt.show()

sns.scatterplot(x="Network size", y="metrics.Partition density", data=df_tmp2)
plt.show()
#%%

link_clust = df_tmp.loc[df_tmp['params.Method'] == 'Link Clustering', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Link Clustering'})
df_tmp = df_tmp.loc[df_tmp['params.Method'] != 'Link Clustering']

df_tmp = df_tmp.merge(link_clust, on='experiment_id')
df_tmp['Improvement'] = df_tmp['metrics.Partition density'] - df_tmp['Link Clustering']
df_tmp = df_tmp[['experiment_id', 'Improvement']]

df_best = df_tmp.groupby('experiment_id')['Improvement'].max().reset_index()

df_tmp2 = df_bal.merge(df_best, on='experiment_id').merge(df_size, on='experiment_id')

sns.scatterplot(x="Balanceness", y="Improvement", data=df_tmp2)
plt.show()

sns.scatterplot(x="Network size", y="Improvement", data=df_tmp2)
plt.show()

#%%








#%%

# Use starttime endtime to calculate the duration and combine it with dt size to make plots

df_stats = df[['run_id', 'experiment_id', 'metrics.Partition density', 'params.Threshold', 'params.Method']]

link_clust = df_stats.loc[df_stats['params.Method'] == 'Link Clustering', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Link Clustering'})
greedy_up = df_stats.loc[df_stats['params.Method'] == 'Greedy algorithm up', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Greedy algorithm up'})
greedy_bottom = df_stats.loc[df_stats['params.Method'] == 'Greedy algorithm bottom', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Greedy algorithm bottom'})
tune = df_stats.loc[df_stats['params.Method'] == 'Tuning dendrogram cut', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Tuning dendrogram cut'})
montecarlo = df_stats.loc[df_stats['params.Method'] == 'Monte Carlo-tuning dendrogram cut', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Monte Carlo simulation'})


dfs = [link_clust, greedy_up, greedy_bottom, tune, montecarlo]
df_final = ft.reduce(lambda left, right: pd.merge(left, right, on='experiment_id'), dfs)
#%%

# Plot the distribution of the normalized partition density
df_tmp = df_final[['Greedy algorithm bottom', 'Greedy algorithm up', 'Tuning dendrogram cut', 'Link Clustering', 'Monte Carlo simulation']]
df_tmp = df_tmp.melt()
df_tmp['value'] = min_max_scaling(df_tmp['value'])

g = sns.kdeplot(data=df_tmp, x="value", hue="variable", fill=True, common_norm=False, alpha=0.4, palette='hls')
sns.move_legend(g, "upper right", title='Method')
plt.xlabel('Normalized Partition density')
plt.ylabel('Probability Density')
plt.show()

#%%

df_final['Greedy bottom - LC'] = df_final['Greedy algorithm bottom'] - df_final['Link Clustering']
df_final['Greedy up - LC'] = df_final['Greedy algorithm up'] - df_final['Link Clustering']
df_final['Tuning - LC'] = df_final['Tuning dendrogram cut'] - df_final['Link Clustering'] 
df_final['MC - LC'] = df_final['Monte Carlo simulation'] - df_final['Link Clustering'] 

#%%
#df_final = df_final[['Greedy bottom - LC', 'Greedy up - LC', 'Tuning - LC', 'MC - LC']]

# Plot the distribution of the difference between each method and the baseline model
df_melt = df_final.melt()

g = sns.kdeplot(data=df_melt, x="value", hue="variable", fill=True, common_norm=False, alpha=0.4, palette='hls')
sns.move_legend(g, "upper left", title='Method')
plt.xlabel('Improvement')
plt.ylabel('Probability Density')
plt.show()

#%%

dt = {'method': ['Greedy bottom', 'Greedy up', 'Tuning', 'Monte Carlo simulation'], 
    'freq of improvement': [len(df_final[df_final['Greedy bottom - LC'] > 0])/df_final.shape[0],
                            len(df_final[df_final['Greedy up - LC'] > 0])/df_final.shape[0],
                            len(df_final[df_final['Tuning - LC'] > 0])/df_final.shape[0],
                            len(df_final[df_final['MC - LC'] > 0])/df_final.shape[0]],
    'freq of decrease': [len(df_final[df_final['Greedy bottom - LC'] < 0])/df_final.shape[0],
                            len(df_final[df_final['Greedy up - LC'] < 0])/df_final.shape[0],
                            len(df_final[df_final['Tuning - LC'] < 0])/df_final.shape[0],
                            len(df_final[df_final['MC - LC'] < 0])/df_final.shape[0]]}

X = dt['method']
improvement = dt['freq of improvement']
decrease = dt['freq of decrease']
  
X_axis = np.arange(len(X))
  
plt.bar(X_axis - 0.2, improvement, 0.4, label = 'freq of improvement')
plt.bar(X_axis + 0.2, decrease, 0.4, label = 'freq of decrease')
  
plt.xticks(X_axis, X)
plt.xlabel("Method")
plt.ylabel("Frequency")
plt.title("Frequency of improvement/decrease for each method")
plt.legend()
plt.show()

#%%

df_corr = df[['run_id', 'experiment_id', 'metrics.Partition density', 'params.Threshold', 'params.Method', 'metrics.Avg- Max entropy sub Real entropy', 'metrics.Avg- Real entropy div Max entropy']]

entr = df_corr[['metrics.Avg- Max entropy sub Real entropy', 'experiment_id']].dropna().reset_index(drop=True)

link_clust = df_corr.loc[df_corr['params.Method'] == 'Link Clustering', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Link Clustering'})
greedy_up = df_corr.loc[df_corr['params.Method'] == 'Greedy algorithm up', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Greedy algorithm up'})
greedy_bottom = df_corr.loc[df_corr['params.Method'] == 'Greedy algorithm bottom', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Greedy algorithm bottom'})
tune = df_corr.loc[df_corr['params.Method'] == 'Tuning dendrogram cut', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Tuning dendrogram cut'})
montecarlo = df_corr.loc[df_corr['params.Method'] == 'Monte Carlo-tuning dendrogram cut', ['metrics.Partition density', 'experiment_id']].reset_index(drop=True).rename(columns={'metrics.Partition density': 'Monte Carlo simulation'})

dfs = [entr, link_clust, greedy_up, greedy_bottom, tune, montecarlo]
df_corrs_final = ft.reduce(lambda left, right: pd.merge(left, right, on='experiment_id'), dfs)


#%%
sns.scatterplot(x="metrics.Avg- Max entropy sub Real entropy", y="Link Clustering", data=df_corrs_final)
plt.show()

sns.scatterplot(x="metrics.Avg- Max entropy sub Real entropy", y="Greedy algorithm up", data=df_corrs_final)
plt.show()

sns.scatterplot(x="metrics.Avg- Max entropy sub Real entropy", y="Greedy algorithm bottom", data=df_corrs_final)
plt.show()

sns.scatterplot(x="metrics.Avg- Max entropy sub Real entropy", y="Tuning dendrogram cut", data=df_corrs_final)
plt.show()

sns.scatterplot(x="metrics.Avg- Max entropy sub Real entropy", y="Monte Carlo simulation", data=df_corrs_final)
plt.show()
#%%

df_corrs_final = df_corrs_final[['metrics.Avg- Max entropy sub Real entropy', 'Link Clustering', 'Greedy algorithm up', 'Greedy algorithm bottom', 'Tuning dendrogram cut', 'Monte Carlo simulation']]
cormat = df_corrs_final.corr()
sns.heatmap(cormat);
#%%
