#%%
# mlflow server --host 0.0.0.0 --port 8888

from methods.link_clustering import *
from methods.greedy_algorithm import *
from methods.tuning_dendrogram_cut import *
from entropy_calc import *
from plots import *
import mlflow
from logger import logger
import os
import shutil


def run_method(exp_id, method, main_path, dataset, delimiter, colors_dict=None, groups=None, level=None, num_edges=None, linkage=None, newcid2cids=None, cid2numedges=None, cid2numnodes=None, orig_cid2edge=None, best_D_LC=None, similarity_LC=None):

    with mlflow.start_run(experiment_id=exp_id):

        mlflow.log_param("Method", method)
        mlflow.log_metric("Dataset size - KB", os.stat(dataset).st_size / 1024)

        # Baseline method - Link Clustering
        if method == "Link Clustering":

            linkage_tmp, list_D_plot, newcid2cids_tmp, orig_cid2edge_tmp, cid2numedges_tmp, cid2numnodes_tmp, num_edges_tmp = link_clustering(filename=dataset, delimiter=delimiter)
            best_D, similarity_value = max(list_D_plot,key=lambda item:item[0])
            mlflow.log_metric('Partition density', best_D)
            mlflow.log_metric('Network size', num_edges_tmp)

            colors_dict_tmp = color_dict(cid2numedges_tmp)
            groups_gen, level_gen, level_entropy = groups_generator(linkage_tmp, newcid2cids_tmp, num_edges_tmp, list_D_plot)
            
            # Entropy calculations
            entropy, max_entropy, sub, avg_sub = entropy_calc(newcid2cids_tmp, num_edges_tmp, level_entropy)
            entropy_plot(entropy, max_entropy, main_path)
            mlflow.log_artifact(main_path+'entropy.png')
            mlflow.log_metric('Balanceness', avg_sub)
            
            best_partitions = level_gen[similarity_value] 
            try:
                imgname = 'link_clustering_dendrogram'
                dendrogram_plot(num_edges=num_edges_tmp, linkage=linkage_tmp, similarity_value=similarity_value, orig_cid2edge=orig_cid2edge_tmp, newcid2cids=newcid2cids_tmp, cid2numedges=cid2numedges_tmp, level=level_gen, colors_dict=colors_dict_tmp, main_path=main_path, imgname=imgname)
            except:
                mlflow.end_run()
                return 0

        elif method == "Greedy algorithm up":
            best_D, best_partitions = greedy_up(num_edges=num_edges, groups=groups, cid2numedges=cid2numedges, cid2numnodes=cid2numnodes)
            mlflow.log_metric('Partition density', best_D)

            try:
                imgname = 'greedy_up_dendrogram'
                dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2numedges=cid2numedges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, colors_dict=colors_dict, main_path=main_path, imgname=imgname) 
            except:
                mlflow.end_run()
                return best_partitions, best_D

        elif method == "Greedy algorithm bottom":
            best_D, best_partitions = greedy_bottom(num_edges=num_edges, groups=groups, orig_cid2edge=orig_cid2edge, newcid2cids=newcid2cids, cid2numedges=cid2numedges, cid2numnodes=cid2numnodes)
            mlflow.log_metric('Partition density', best_D)

            try:
                imgname = 'greedy_bottom_dendrogram'
                dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2numedges=cid2numedges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, colors_dict=colors_dict, main_path=main_path, imgname=imgname)
            except:
                mlflow.end_run()
                return best_partitions, best_D

        elif method == 'Tuning dendrogram cut':

            threshold = 10000 
            stopping_threshold = 5

            list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2numedges=cid2numedges, cid2numnodes=cid2numnodes, level=level, similarity_value=similarity_LC, best_D=best_D_LC, threshold=threshold, stopping_threshold=stopping_threshold)

            best_D = list(list_D.values())[-1]
            mlflow.log_metric('Partition density', best_D)

            imgname1 = f'partitiondensity_{threshold}'
            imgname2 = f'clusters_{threshold}'
            tuning_metrics(list_D=list_D, list_clusters=list_clusters, threshold=threshold, main_path=main_path, imgname1=imgname1, imgname2=imgname2)
            mlflow.log_artifact(main_path+imgname1+'.png')
            mlflow.log_artifact(main_path+imgname2+'.png')

            mlflow.log_param('Threshold', threshold)

            try:
                imgname = f'tuning_dendrogram_cut_{threshold}'
                dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2numedges=cid2numedges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, colors_dict=colors_dict, main_path=main_path, imgname=imgname) 
            except:
                mlflow.end_run()
                return best_partitions, best_D


        elif method == 'Monte Carlo-tuning dendrogram cut':

            threshold = 10000
            epsilon = [0.1, 0.05, 0.01, 0.001, 0] 

            list_D, list_clusters, best_partitions = tune_cut(num_edges=num_edges, groups=groups, newcid2cids=newcid2cids, cid2numedges=cid2numedges, cid2numnodes=cid2numnodes, level=level, similarity_value=similarity_LC, best_D=best_D_LC, threshold=threshold, montecarlo=True, epsilon=epsilon)

            best_D = list(list_D.values())[-1]
            mlflow.log_metric('Partition density', best_D)
            
            imgname1 = f'montecarlo_partitiondensity_{threshold}'
            imgname2 = f'montecarlo_clusters_{threshold}'
            tuning_metrics(list_D=list_D, list_clusters=list_clusters, threshold=threshold, main_path=main_path, imgname1=imgname1, imgname2=imgname2)
            mlflow.log_artifact(main_path+imgname1+'.png')
            mlflow.log_artifact(main_path+imgname2+'.png')

            mlflow.log_param('Threshold', threshold)

            try:
                imgname = f'montecarlo_tuning_dendrogram_cut_{threshold}'
                dendrogram_greedy(linkage=linkage, best_partitions=best_partitions, cid2numedges=cid2numedges, newcid2cids=newcid2cids, orig_cid2edge=orig_cid2edge, colors_dict=colors_dict, main_path=main_path, imgname=imgname)
            except:
                mlflow.end_run()
                return best_partitions, best_D

        else: 
            logger.warning('Unknown method...End of experiment')
            return 0

        mlflow.log_metric('Partition density', best_D)

        mlflow.log_artifact(main_path+imgname+'.png')

        if method == 'Turing dendrogram cut' or method == 'Monte Carlo-turing dendrogram cut':
            mlflow.log_artifact(main_path+imgname1+'.png')
            mlflow.log_artifact(main_path+imgname2+'.png')

    mlflow.end_run()
    

    if method == 'Link Clustering':
        return best_partitions, best_D, similarity_value, num_edges_tmp, linkage_tmp, orig_cid2edge_tmp, cid2numnodes_tmp, cid2numedges_tmp, newcid2cids_tmp, colors_dict_tmp, groups_gen, level_gen
    else:
        return best_partitions, best_D



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

            # else:
            #     logger.warning('Already tested... Continue')
            #     continue

            try:
                exp_id = mlflow.create_experiment(name=experiment_name)
            except Exception as e:
                exp_id = mlflow.get_experiment_by_name(name=experiment_name).experiment_id

            logger.warning('Experiment created.')

            partitions = {}
            part_dens = {}

            method = 'Link Clustering'
            logger.warning(f'Running method: {method}')
            partitions[method], part_dens[method], similarity_value, num_edges, linkage, orig_cid2edge, cid2numnodes, cid2numedges, newcid2cids, colors_dict, groups, level = run_method(exp_id=exp_id, method=method, main_path=main_path, dataset=dataset, delimiter=delimiter)
            logger.warning(f'Method done!')

            methods = ['Greedy algorithm up', 'Greedy algorithm bottom', 'Tuning dendrogram cut', 'Monte Carlo-tuning dendrogram cut']

            for method in methods[:2]:
                logger.warning(f'Running method: {method}')
                partitions[method], part_dens[method] = run_method(exp_id=exp_id, method=method, main_path=main_path, dataset=dataset, delimiter=delimiter, colors_dict=colors_dict, groups=groups, num_edges=num_edges, linkage=linkage, newcid2cids=newcid2cids, cid2numedges=cid2numedges, cid2numnodes=cid2numnodes, orig_cid2edge=orig_cid2edge)
                logger.warning(f'Method done!')

            for method in methods[2:]:
                logger.warning(f'Running method: {method}')
                partitions[method], part_dens[method] = run_method(exp_id=exp_id, method=method, main_path=main_path, dataset=dataset, delimiter=delimiter, colors_dict=colors_dict, groups=groups, level=level, num_edges=num_edges, linkage=linkage, newcid2cids=newcid2cids, cid2numedges=cid2numedges, cid2numnodes=cid2numnodes, orig_cid2edge=orig_cid2edge, best_D_LC=part_dens['Link Clustering'], similarity_LC=similarity_value)
                logger.warning(f'Method done!')

            #graph_plot(partitions, part_dens, dataset, delimiter, num_edges, colors_dict, cid2numedges, newcid2cids, main_path)

        except Exception as e:

            error_dir = 'data/error_data/'

            if not os.path.exists(error_dir):
                    os.makedirs(error_dir)

            err_file = open(error_dir+f"Error_{file[:-4]}.txt", "w")
            n = err_file.write(str(e))
            err_file.close()
#%%