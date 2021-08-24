# hamzadugmag/forcolab-clustering
# torrent.eecg.utoronto.ca

import hdbscan

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE

import math
import time
import os


def run(prop, name, iterations=10000, max_minpts=500, is_allowing_single_cluster=False, max_prob=0.05):
    """
    Cluster community posts in raw_data.csv using HDBSCAN and plot the dendrograms, boxplots per cluster, and TSNE plots

    prop: property to cluster by
        0: length
        1: activity
        2: popularity
        3: structure
        4: all properties

    name: property label
    iterations: TSNE iterations
    max_minpts: Range to check for optimal HDBSCAN min_cluster_size
    is_allowing_single_cluster: HDBSCAN allow_single_cluster
    max_prob: cutoff probability for optimizing min_cluster_size
    """

    start = time.time()
    LOG("\n" + name + " STARTED")

    try:
        os.mkdir(name)  # organize plots in same folder
    except Exception:
        pass

    # ===================================================================================================================== EXTRACT
    # lists of properties (length, activity, popularity, structure)
    l_cols = ["Text Length", "No. of SO Links", "No. of ALL Links", "ALL - SO", "SO / ALL"]
    a_cols = ["No. of Revisions", "Creation Date", "Last Update Time", "No. of Contributers", "Creation - Updated"]
    p_cols = ["No. of Upvotes", "zeros"]  # need at least two features per property to work with pandas efficiently
    s_cols = ["No. of Headings", "Avg. No. of SO Links / Heading"]

    df = pd.read_csv("raw_data.csv")  # raw data

    # extract properties into separate dataframes
    df_length = pd.DataFrame(columns=l_cols)
    df_length[l_cols] = df["length"].str.split("\\|\\|", expand=True)

    df_activity = pd.DataFrame(columns=a_cols)
    df_activity[a_cols] = df["activity"].str.split("\\|\\|", expand=True)

    df_popularity = pd.DataFrame(columns=p_cols)
    df_popularity[p_cols[0]] = df["popularity"].copy()
    df_popularity[p_cols[1]] = np.zeros((df.shape[0], 1))  # deleted later

    df_structure = pd.DataFrame(columns=s_cols)
    df_structure[s_cols] = df["structure"].str.split("\\|\\|", expand=True)

    # combine dataframes
    df_all = pd.concat([df_length, df_activity, df_popularity, df_structure], axis=1)
    df_all = df_all.astype(np.float16)

    # ===================================================================================================================== PREPARE
    # # random sample for testing
    # shuffled = df_all.sample(frac=1)
    # samples = np.array_split(shuffled, 20)
    # data_unscaled = samples[0]

    data_unscaled = df_all.copy()

    columns = [l_cols, a_cols, p_cols, s_cols, df_all.columns]

    data = data_unscaled[columns[prop]].copy()
    data[data.columns] = MinMaxScaler().fit_transform(data[data.columns])  # normalize data

    try:
        del data["zeros"]
    except Exception:
        pass

    LOG(name + " READY")

    # ===================================================================================================================== TSNE
    perp = round(data.shape[0]**0.5)  # optimize perplexity
    plt.title("TSNE Plot Perplexity = " + str(perp))
    projection = TSNE(perplexity=perp, n_iter=iterations).fit_transform(data)
    plt.scatter(*projection.T, s=50, linewidth=0, alpha=0.25)
    plt.savefig(name + "/" + name + "_tsne_unclustered.png")
    plt.clf()
    LOG(name + " TSNE")

    # ===================================================================================================================== HDBSCAN OPT
    min_pts = list(range(2, max_minpts))
    trials = 1

    scores = []

    for min_pt in min_pts:
        score = 0
        for trial in range(trials):
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_pt, allow_single_cluster=is_allowing_single_cluster).fit(data)
            score += len([prob for prob in clusterer.probabilities_ if prob < max_prob]) / data.shape[0]

        score /= trials
        scores.append(score)

    log_scores = [math.log10(score + 1) for score in scores]
    answer = min_pts[log_scores.index(min(log_scores))]  # optimize min_cluster_size

    plt.plot(min_pts, log_scores)
    plt.title("Optimal Minimum Cluster Size = " + str(answer))
    plt.xlabel("Minimum Cluster Size")
    plt.ylabel("LOG(score)")
    plt.savefig(name + "/" + name + "_minpts_minimization.png")
    plt.clf()
    LOG(name + " OPTIMAL MINIMUM CLUSTER SIZE")

    # ===================================================================================================================== HDBSCAN
    # now cluster using optimal min_cluster_size
    clusterer = hdbscan.HDBSCAN(min_cluster_size=answer, allow_single_cluster=is_allowing_single_cluster).fit(data)
    cluster_labels = clusterer.labels_
    data_unscaled["Cluster"] = cluster_labels
    n_clusters = max(cluster_labels) + 1
    LOG(name + " HDBSCAN")

    # ===================================================================================================================== DENDRO
    clusterer.condensed_tree_.plot(select_clusters=True)
    plt.title("Dendrogram")
    plt.savefig(name + "/" + name + "_dendrogram.png")
    plt.clf()
    LOG(name + " DENDROGRAM")

    # ===================================================================================================================== TSNE CLUSTER
    plt.title("TSNE Cluster Plot Perplexity = " + str(perp))
    plt.scatter(*projection.T, c=cluster_labels, cmap="tab10", s=50, linewidth=0, alpha=0.25)  # color clusters
    plt.savefig(name + "/" + name + "_tsne_clustered.png")
    plt.clf()
    LOG(name + " CLUSTER PLOT")

    # ===================================================================================================================== BOX
    c_id = data_unscaled.shape[1] - 1  # "cluster" column number is last column
    titles = list(data_unscaled.columns.values)

    for i in range(n_clusters):  # for each cluster
        fig, axes = plt.subplots(nrows=1, ncols=data_unscaled.shape[1]-1, sharex=True, sharey=False)  # prepare cluster boxplot
        fig.suptitle("Cluster " + str(i) + " Boxplots")
        fig.set_figwidth(45)
        for j in range(len(axes)):
            vals = data_unscaled[data_unscaled[data_unscaled.columns[c_id]] == i][data_unscaled.columns[j]]  # get ith column in cluster c_id
            axes[j].boxplot(vals, showfliers=True)
            axes[j].set_title(titles[j])
            axes[j].set_xticks([])

        fig.tight_layout()
        plt.savefig(name + "/" + name + "_cluster" + str(i) + "boxplots.png")
        plt.close(fig)

    LOG(name + " BOXPLOTS")

    # ===================================================================================================================== CSV
    data_unscaled["Post ID"] = df["post_id"]  # add post_id

    cols = list(data_unscaled.columns)
    cols = [cols[-1]] + cols[:-1]
    data_unscaled = data_unscaled[cols]  # shift post_id to first column

    data_unscaled.to_csv(name + "/" + name + "_hdbscan_optimized_results.csv", encoding='utf-8', index=False)
    LOG(name + " CSV")

    # ===================================================================================================================== DONE
    end = time.time()
    LOG(name + " FINISHED IN " + str(round(end - start, 2)) + "s")


def LOG(text):
    """
    Write text to log.txt and print in terminal
    """
    f = open("log.txt", "a")
    f.write(text + "\n")
    f.close()
    print(text)


LOG("\n====== STARTING ======")
run(4, "ALL")
run(3, "STRUCTURE")
run(2, "POPULARITY")
run(1, "ACTIVITY")
run(0, "LENGTH")
LOG("\n====== FINISHED ======\n")
