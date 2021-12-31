from Helper.common import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from sklearn.externals import joblib


class PreDescCluster:
    def __init__(self, desc_path, cluster_num):
        self.scores = []
        self.true_ks = []
        self.desc_path = desc_path
        self.k = cluster_num

    def start(self):
        files = getFileList(self.desc_path, ".txt")
        #self.cluster_test(files)
        # self.draw_plot()
        self.cluster(files)

    def cluster(self, documents):
        vector_path = 'tfidf_fit_result.pkl'
        km_path = 'km_cluster_fit_result.pkl'
        weight_path = 'weight_result.pkl'

        if os.path.exists(vector_path) and os.path.exists(km_path) and os.path.exists(weight_path):
            vectorizer = joblib.load(vector_path)
            clf = joblib.load(km_path)
            weight = joblib.load(weight_path)
        else:
            # vectorizer = TfidfVectorizer(input='filename', max_features=10000)
            vectorizer = TfidfVectorizer(input='filename')
            tfidf = vectorizer.fit_transform(documents)
            weight = tfidf.toarray()
            clf = KMeans(n_clusters=self.k)
            clf.fit(weight)
            joblib.dump(weight, weight_path)
            joblib.dump(vectorizer, vector_path)
            joblib.dump(clf, km_path)

        self.showable("cluster_showable.txt", clf, vectorizer, self.k)
        # Labels of each point
        m_clusters = clf.labels_.tolist()  # 获取聚类标签
        num_count = {}
        for item in m_clusters:
            if item in num_count:
                num_count[item] += 1
            else:
                num_count[item] = 1

        with open("num_count.txt", "w") as fw:
            for item in num_count:
                fw.write(str(item) + " " + str(num_count[item]) + "\n")

        with open("cluster_label.csv", "w") as fw:
            writer = csv.writer(fw)
            writer.writerow(["sha256", "cluster"])
            for i in range(len(m_clusters)):
                file = documents[i]
                sha256 = os.path.split(file)[-1][:-4]
                writer.writerow([sha256, str(m_clusters[i])])

        closest, _ = pairwise_distances_argmin_min(clf.cluster_centers_, weight)

        with open("cluster_center.csv", "w") as fw:
            writer = csv.writer(fw)
            writer.writerow(["sha256", "cluster"])
            for item in closest:
                file = documents[item]
                sha256 = os.path.split(file)[-1][:-4]
                cluster_label = m_clusters[item]
                writer.writerow([sha256, str(cluster_label)])

    def cluster_test(self, documents):
        vectorizer = TfidfVectorizer(input='filename', max_features=10000)
        tfidf = vectorizer.fit_transform(documents)
        # pairwise_similarity = (tfidf * tfidf.T).toarray()
        # Extract the tf-idf matrix, and the element w[i][j]
        # represents the tf-idf weight of the j word in the type i text
        weight = tfidf.toarray()
        length = len(documents)
        for k in range(150, 200, 1):
            clf, score = self.one_cluster(weight, k)
            avg_score = round(1.0 * score / length, 4)
            with open("scores.txt", "a+") as fw:
                fw.write(str(k) + " " + str(avg_score) + "\n")
            self.true_ks.append(k)
            self.scores.append(avg_score)

    def one_cluster(self, weight, true_k):
        print("Start KMeans:")
        clf = KMeans(n_clusters=true_k)
        clf.fit(weight)
        # inertia_ : float
        # Sum of distances of samples to their closest cluster center.
        return clf, clf.inertia_

    def draw_plot(self):
        plt.figure(figsize=(8, 4))
        plt.plot(self.true_ks, self.scores, label="error", color="red", linewidth=1)
        plt.xlabel("K value")
        plt.ylabel("Sum of distances")
        plt.legend()
        plt.savefig('error_detail1.pdf')

    def showable(self, filename, clf, vectorizer, k):
        order_centroids = clf.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        with open(filename, "w") as fw:
            for i in range(k):
                fw.write("Cluster %d:" % i)
                for ind in order_centroids[i, :10]:
                    fw.write(' %s' % terms[ind])
                fw.write("\n")


if __name__ == '__main__':
    cluster_num = 157
    desc_path = "/home/username/APIRecommendation/Description_presolved"
    preDescCluster = PreDescCluster(desc_path, cluster_num)
    preDescCluster.start()
