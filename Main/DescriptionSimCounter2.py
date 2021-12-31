import re
import threadpool
from Helper.common import *
import torch
from flair.data import Sentence
from flair.embeddings import FlairEmbeddings, DocumentPoolEmbeddings, WordEmbeddings
import os
from nltk.corpus import stopwords


class DescriptionSimCounter2:
    def __init__(self, OPTIONS, custom_args, size):
        self.embeddings = DocumentPoolEmbeddings(
            [WordEmbeddings('glove'), FlairEmbeddings('news-forward'), FlairEmbeddings('news-backward')])
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.max_jobs = 5
        self.size = size
        self.english_stopwords = stopwords.words("english")
        self.trainingset = []  # training file name
        self.trainingset_length = 0
        self.documents = []  # Sentence()

    def processone(self, file):
        filename = os.path.split(file)[-1][:-4]
        test_desc_path = os.path.join(self.OPTIONS.description, filename + ".txt")
        if os.path.exists(os.path.join(self.custom_args['Training_Set_filtered'], filename + ".csv")):
            return
        try:
            print("[+] Description analysis of " + filename)
            sim_map = {}
            flag = False
            for i in range(self.trainingset_length):
                score = self.cos_sim(test_desc_path, self.documents[i])
                sim_map[self.trainingset[i]] = score
                if score:
                    flag = True
            if flag:
                # sim_lst = dict2sortedlist(sim_map)[:self.size]
                sim_lst = dict2sortedlist(sim_map)
                headings = ['Training file', 'similarity']
                writeScores(self.custom_args['Training_Set_filtered'], filename, sim_lst, headings)

        except Exception as e:
            print(e)
            return

    def cos_sim(self, query_path, train):
        with open(query_path, "r") as fr:
            content = fr.read()
        query = Sentence(content)
        self.embeddings.embed(query)
        # use cosine distance
        cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)
        # get similarity between embeddings of query and paragraph 1
        similarity = cos(query.embedding, train.embedding)
        return round(similarity.item(), 6)

    def load_trainingset(self):
        training_set = self.custom_args['Training_Set']
        train_files = getFileList_from_txt(training_set)
        for train_file in train_files:
            self.trainingset.append(train_file)
        self.trainingset_length = len(self.trainingset)

    def embed(self):
        for filename in self.trainingset:
            train_file = os.path.join(self.OPTIONS.description, filename + ".txt")
            with open(train_file, "r") as fr:
                content = fr.read()
            paragraph = Sentence(content)
            self.documents.append(paragraph)
            self.embeddings.embed(paragraph)
        print("[+] Embedded done.")

    def start(self):
        self.load_trainingset()
        self.embed()
        apks = getFileList(self.custom_args['Test_Set'], ".csv")
        print("[+] Total test apks ", len(apks))
        print("[+] Saving filtered results to " + self.custom_args['Training_Set_filtered'])
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.processone, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()
