import threadpool
from Helper.common import *


class DescriptionCluster:
    def __init__(self, OPTIONS, custom_args, size, cluster_label_path):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.max_jobs = 5
        self.size = size
        self.cluster = {}
        self.train_set = []
        self.cluster_label_path = cluster_label_path

    def processone(self, file):
        filename = os.path.split(file)[-1][:-4]
        same_cluster_file = []
        if os.path.exists(os.path.join(self.custom_args['Training_Set_filtered'], filename + ".csv")):
            return
        try:
            print("[+] Cluster analysis of " + filename)
            sim_map = {}
            testfile_label = self.cluster[filename]
            for item in self.cluster:
                if self.cluster[item] == testfile_label and item in self.train_set:
                    same_cluster_file.append(item)
                    sim_map[item] = 1
            if len(same_cluster_file) >= self.size:
                sim_lst = dict2sortedlist(sim_map)
                headings = ['Training file', 'similarity']
                writeScores(self.custom_args['Training_Set_filtered'], filename, sim_lst, headings)

        except Exception as e:
            print(e)
            return

    def read_cluster(self, cluster_file):
        with open(cluster_file, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                sha256 = line[0]
                label = line[1]
                self.cluster[sha256] = label

    def start(self):
        self.read_cluster(self.cluster_label_path)
        apks = getFileList(self.custom_args['Test_Set'], ".csv")
        self.train_set = getFileList_from_txt(self.custom_args['Training_Set'])

        print("[+] Saving filtered results to " + self.custom_args['Training_Set_filtered'])
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.processone, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

