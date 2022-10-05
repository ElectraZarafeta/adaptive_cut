#%%

# mlflow server --host 0.0.0.0 --port 8888

from methods.link_clustering import link_clustering
from methods.greedy_algorithm import *
from methods.tuning_dendrogram_cut import *
from plots import *
import mlflow
from logger import logger

dataset = 'data/lesmis_unweighted.txt'
delimiter = '-'

experiment_name = 'Les Miserables dataset'
main_path = 'output/imgs/lesmis/'

try:
    exp_id = mlflow.create_experiment(name=experiment_name)
except Exception as e:
    exp_id = mlflow.get_experiment_by_name(name=experiment_name).experiment_id


def run_method(exp_id, method, main_path, dataset, delimiter):

    with mlflow.start_run(experiment_id=exp_id):

        mlflow.log_param("Method", method)

        linkage, list_D_plot, groups, newcid2cids, orig_cid2edge, cid2edges, cid2nodes, num_edges = link_clustering(filename=dataset, delimiter=delimiter)
        best_D_bl, similarity_value = max(list_D_plot,key=lambda item:item[0])

        if method == "Link Clustering":
            best_D = best_D_bl

            imgname = 'link_clustering_dendrogram'
            dendrogram_plot(num_edges=num_edges, linkage=linkage, similarity_value=similarity_value, orig_cid2edge=orig_cid2edge, main_path=main_path, imgname=imgname)

        elif method == "Greedy algorithm up":
            best_D, best_partitions = greedy_up(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, linkage=linkage, cid2edges=cid2edges, cid2nodes=cid2nodes)
            
            imgname = 'greedy_up_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, main_path=main_path, imgname=imgname) 

        elif method == "Greedy algorithm bottom":
            best_D, best_partitions = greedy_bottom(num_edges=num_edges, groups=groups, orig_cid2edge=orig_cid2edge, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes)

            imgname = 'greedy_bottom_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, main_path=main_path, imgname=imgname)

        elif method == 'Turing dendrogram cut':

            threshold = 5000 
            stopping_threshold = 5

            list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes, linkage=linkage, similarity_value=similarity_value, best_D=best_D_bl, threshold=threshold, stopping_threshold=stopping_threshold)

            best_D = list(list_D.values())[-1]

            imgname = f'tuning_dendrogram_cut_{threshold}'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, main_path=main_path, imgname=imgname)

            imgname1 = f'partitiondensity_{threshold}'
            imgname2 = f'clusters_{threshold}'
            tuning_metrics(list_D=list_D, list_clusters=list_clusters, threshold=threshold, main_path=main_path, imgname1=imgname1, imgname2=imgname2)

            mlflow.log_metric('Threshold', threshold)

        else:

            threshold = 10000
            epsilon = [0.2, 0.1, 0.05, 0.01, 0.001, 0]

            list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes, linkage=linkage, similarity_value=similarity_value, best_D=best_D_bl, threshold=threshold, montecarlo=True, epsilon=epsilon)

            best_D = list(list_D.values())[-1]

            imgname = f'montecarlo_tuning_dendrogram_cut_{threshold}'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, main_path=main_path, imgname=imgname)

            imgname1 = f'montecarlo_partitiondensity_{threshold}'
            imgname2 = f'montecarlo_clusters_{threshold}'
            tuning_metrics(list_D=list_D, list_clusters=list_clusters, threshold=threshold, main_path=main_path, imgname1=imgname1, imgname2=imgname2)

            mlflow.log_metric('Threshold', threshold)

        mlflow.log_metric('Partition density', best_D)

        mlflow.log_artifact(main_path+imgname+'.png')

        if method == 'Turing dendrogram cut' or method == 'Monte Carlo-turing dendrogram cut':
            mlflow.log_artifact(main_path+imgname1+'.png')
            mlflow.log_artifact(main_path+imgname2+'.png')

    mlflow.end_run()


methods = ['Link Clustering', 'Greedy algorithm up', 'Greedy algorithm bottom', 'Turing dendrogram cut', 'Monte Carlo-turing dendrogram cut']

run_method(exp_id=exp_id, method=methods[4], main_path=main_path, dataset=dataset, delimiter=delimiter)

#%%

for method in methods:
    run_method(exp_id=exp_id, method=method, main_path=main_path, dataset=dataset, delimiter=delimiter)

#%%