#%%

# mlflow server --host 0.0.0.0 --port 8888

from link_clustering import link_clustering
from greedy_algorithm import *
from tuning_dendrogram_cut import *
from plots import *
import mlflow

dataset = 'data/facebook.txt'
delimiter = '-'
imgname_dt = 'fb'

experiment_name = 'Facebook dataset'

threshold = 1500 #100 for lesmis
stopping_threshold = 5

try:
    exp_id = mlflow.create_experiment(name=experiment_name)
except Exception as e:
    exp_id = mlflow.get_experiment_by_name(name=experiment_name).experiment_id


def run_method(exp_id, method, imgname_dt, dataset, delimiter):

    with mlflow.start_run(experiment_id=exp_id):

        mlflow.log_param("Method", method)

        linkage, list_D_plot, groups, newcid2cids, orig_cid2edge, cid2edges, cid2nodes, num_edges = link_clustering(filename=dataset, delimiter=delimiter)
        best_D_bl, similarity_value = max(list_D_plot,key=lambda item:item[0])

        if method == "Link Clustering":

            imgname = imgname_dt+'_link_clustering_dendrogram'
            dendrogram_plot(num_edges=num_edges, linkage=linkage, similarity_value=similarity_value, orig_cid2edge=orig_cid2edge, imgname=imgname)

        elif method == "Greedy algorithm up":
            best_D, best_partitions = greedy_up(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, linkage=linkage, cid2edges=cid2edges, cid2nodes=cid2nodes)
            
            imgname = imgname_dt+'_greedy_up_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, imgname=imgname) 

        elif method == "Greedy algorithm bottom":
            best_D, best_partitions = greedy_bottom(num_edges=num_edges, groups=groups, orig_cid2edge=orig_cid2edge, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes)

            imgname = imgname_dt+'_greedy_bottom_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, imgname=imgname)

        else:

            list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes, linkage=linkage, similarity_value=similarity_value, best_D=best_D_bl, threshold=threshold, stopping_threshold=stopping_threshold)

            best_D = list(list_D.values())[-1]

            imgname = imgname_dt+'_tuning_dendrogram_cut'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, imgname=imgname)

            imgname1 = imgname_dt+'_partitiondensity'
            imgname2 = imgname_dt+'_clusters'
            tuning_metrics(list_D=list_D, list_clusters=list_clusters, threshold=threshold, imgname1=imgname1, imgname2=imgname2)

        mlflow.log_metric('Best partition density', best_D)

        mlflow.log_artifact('output/imgs/'+imgname+'.png')

        if method == 'Turing dendrogram cut':
            mlflow.log_artifact('output/imgs/'+imgname1+'.png')
            mlflow.log_artifact('output/imgs/'+imgname2+'.png')

    mlflow.end_run()


methods = ['Link Clustering', 'Greedy algorithm up', 'Greedy algorithm bottom', 'Turing dendrogram cut']

run_method(exp_id=exp_id, method=methods[3], imgname_dt=imgname_dt, dataset=dataset, delimiter=delimiter)

#%%

for method in methods:
    run_method(exp_id=exp_id, method=method, imgname_dt=imgname_dt, dataset=dataset, delimiter=delimiter)


#%%