#%%
# mlflow server --host 0.0.0.0 --port 8888

from methods.link_clustering import link_clustering
from methods.greedy_algorithm import *
from methods.tuning_dendrogram_cut import *
from entropy_calc import *
from plots import *
import mlflow
from logger import logger
import os
import shutil


def run_method(exp_id, method, main_path, dataset, delimiter, colors_dict=None):

    with mlflow.start_run(experiment_id=exp_id):

        mlflow.log_param("Method", method)

        # Baseline method - Link Clustering
        linkage, list_D_plot, groups, newcid2cids, orig_cid2edge, cid2edges, cid2nodes, num_edges = link_clustering(filename=dataset, delimiter=delimiter)
        best_D_bl, similarity_value = max(list_D_plot,key=lambda item:item[0])

        if method == "Link Clustering":

            colors_dict_tmp = color_dict(cid2edges)

            entropy = entropy_calc(linkage, newcid2cids, num_edges)
            entropy_plot(entropy, main_path)
            mlflow.log_artifact(main_path+'entropy.png')
            
            T = hierarchy.fcluster(np.array(linkage), t=similarity_value, criterion='distance')
            best_partitions = hierarchy.leaders(np.array(linkage), T)[0].tolist()

            best_D = best_D_bl

            imgname = 'link_clustering_dendrogram'
            dendrogram_plot(num_edges=num_edges, linkage=linkage, similarity_value=similarity_value, orig_cid2edge=orig_cid2edge, newcid2cids=newcid2cids, cid2edges=cid2edges, colors_dict=colors_dict_tmp, main_path=main_path, imgname=imgname)

        elif method == "Greedy algorithm up":
            best_D, best_partitions = greedy_up(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, linkage=linkage, cid2edges=cid2edges, cid2nodes=cid2nodes)

            imgname = 'greedy_up_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, colors_dict=colors_dict, main_path=main_path, imgname=imgname) 

        elif method == "Greedy algorithm bottom":
            best_D, best_partitions = greedy_bottom(num_edges=num_edges, groups=groups, orig_cid2edge=orig_cid2edge, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes)

            imgname = 'greedy_bottom_dendrogram'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, colors_dict=colors_dict, main_path=main_path, imgname=imgname)

        elif method == 'Tuning dendrogram cut':

            threshold = 5000 
            stopping_threshold = 5

            list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes, linkage=linkage, similarity_value=similarity_value, best_D=best_D_bl, threshold=threshold, stopping_threshold=stopping_threshold)


            best_D = list(list_D.values())[-1]

            imgname = f'tuning_dendrogram_cut_{threshold}'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, colors_dict=colors_dict, main_path=main_path, imgname=imgname)

            imgname1 = f'partitiondensity_{threshold}'
            imgname2 = f'clusters_{threshold}'
            tuning_metrics(list_D=list_D, list_clusters=list_clusters, threshold=threshold, main_path=main_path, imgname1=imgname1, imgname2=imgname2)

            mlflow.log_param('Threshold', threshold)

        else:

            threshold = 500
            epsilon = [0.2, 0.1, 0.05, 0.01, 0.001, 0]

            list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2edges=cid2edges, cid2nodes=cid2nodes, linkage=linkage, similarity_value=similarity_value, best_D=best_D_bl, threshold=threshold, montecarlo=True, epsilon=epsilon)

            best_D = list(list_D.values())[-1]

            imgname = f'montecarlo_tuning_dendrogram_cut_{threshold}'
            dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2edges=cid2edges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, main_path=main_path, imgname=imgname)

            imgname1 = f'montecarlo_partitiondensity_{threshold}'
            imgname2 = f'montecarlo_clusters_{threshold}'
            tuning_metrics(list_D=list_D, list_clusters=list_clusters, threshold=threshold, main_path=main_path, imgname1=imgname1, imgname2=imgname2)

            mlflow.log_param('Threshold', threshold)

        mlflow.log_metric('Partition density', best_D)

        mlflow.log_artifact(main_path+imgname+'.png')

        if method == 'Turing dendrogram cut' or method == 'Monte Carlo-turing dendrogram cut':
            mlflow.log_artifact(main_path+imgname1+'.png')
            mlflow.log_artifact(main_path+imgname2+'.png')

    mlflow.end_run()


    if method == 'Link Clustering':
        return best_partitions, best_D, num_edges, cid2edges, newcid2cids, colors_dict_tmp
    else:
        return best_partitions, best_D, num_edges, cid2edges, newcid2cids

length = len(os.listdir('data/'))

for step, file in enumerate(os.listdir('data/')):

    f = os.path.join('data/', file)

    if os.path.isfile(f):

        try:
            
            experiment_name = file[:-4]
            logger.warning(f'### EXPERIMENT ({step+1}/{length}): {experiment_name} ###')

            dataset = f'data/{experiment_name}.txt'
            delimiter = '-'

            main_path = f'output/imgs/{experiment_name}/'

            if not os.path.exists(main_path):
                os.makedirs(main_path)

            else:
                logger.warning('Already tested... Continue')
                continue

            try:
                exp_id = mlflow.create_experiment(name=experiment_name)
            except Exception as e:
                exp_id = mlflow.get_experiment_by_name(name=experiment_name).experiment_id

            logger.warning('Experiment created.')

            partitions = {}
            part_dens = {}

            method = 'Link Clustering'
            logger.warning(f'Running method: {method}')
            best_partitions, best_D, num_edges, cid2edges, newcid2cids, colors_dict = run_method(exp_id=exp_id, method=method, main_path=main_path, dataset=dataset, delimiter=delimiter)
            logger.warning(f'Method done!')
            partitions[method] = best_partitions
            part_dens[method] = best_D

            methods = ['Greedy algorithm up', 'Greedy algorithm bottom', 'Tuning dendrogram cut'] #, 'Monte Carlo-turing dendrogram cut']

            for method in methods:
                logger.warning(f'Running method: {method}')
                best_partitions, best_D, num_edges, cid2edges, newcid2cids = run_method(exp_id=exp_id, method=method, main_path=main_path, dataset=dataset, delimiter=delimiter, colors_dict=colors_dict)
                logger.warning(f'Method done!')
                partitions[method] = best_partitions
                part_dens[method] = best_D

            graph_plot(partitions, part_dens, dataset, delimiter, num_edges, colors_dict, cid2edges, newcid2cids, main_path)
        
        except:
            shutil.move('data/' + file, 'error_data/' + file)

            logger.warning(f'{file} moved to error_data directory')
            os.rmdir(main_path)
#%%