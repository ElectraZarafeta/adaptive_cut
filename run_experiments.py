#%%

from link_clustering import link_clustering
from greedy_algorithm import *
from plots import *
import mlflow

dataset = 'data/facebook.txt'
delimiter = '-'
imgname_dt = 'fb'

experiment_name = 'Facebook dataset'

try:
    exp_id = mlflow.create_experiment(name=experiment_name)
except Exception as e:
    exp_id = mlflow.get_experiment_by_name(name=experiment_name).experiment_id


def run_method(exp_id, method, imgname_dt, dataset, delimiter):

    with mlflow.start_run(experiment_id=exp_id):

        mlflow.log_param("Method", method)

        linkage, list_D_plot, groups, newcid2cids, orig_cid2edge, cid2edges, cid2nodes, num_edges = link_clustering(filename=dataset, delimiter=delimiter)

        if method == "Link Clustering":
            
            best_D, similarity_value = max(list_D_plot,key=lambda item:item[0])

            imgname = imgname_dt+'_link_clustering_dendrogram'
            dendrogram_plot(num_edges=num_edges, linkage=linkage, similarity_value=similarity_value, orig_cid2edge=orig_cid2edge, imgname=imgname)

        elif method == "Greedy algorithm up":
            best_D, best_partitions = greedy_up(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, linkage=linkage, cid2edges=cid2edges, cid2nodes=cid2nodes)
            
            imgname = imgname_dt+'_greedy_up_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, imgname=imgname) 

        else:
            best_D, best_partitions = greedy_bottom(num_edges=num_edges, groups=groups, orig_cid2edge=orig_cid2edge, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes)

            imgname = imgname_dt+'_greedy_bottom_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, imgname=imgname)


        mlflow.log_metric('Best partition density', best_D)

        mlflow.log_artifact('output/imgs/'+imgname+'.png')

    mlflow.end_run()


#run_method(exp_id=exp_id, method='Greedy algorithm bottom', imgname_dt=imgname_dt, dataset=dataset, delimiter=delimiter)

#%%

methods = ['Link Clustering', 'Greedy algorithm up', 'Greedy algorithm bottom']

for method in methods:
    run_method(exp_id=exp_id, method=method, imgname_dt=imgname_dt, dataset=dataset, delimiter=delimiter)


#%%