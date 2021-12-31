import re
import threadpool
from Helper.common import *
import string
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

# nltk.download('stopwords')
# nltk.download('punkt')

class DescriptionSimCounter:
    def __init__(self, OPTIONS, custom_args, Threshold):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.max_jobs = 5
        self.Threshold = Threshold
        self.english_stopwords = stopwords.words("english")

    # def cosine_sim(self, documents):
    #     # vectorizer = TfidfVectorizer(tokenizer=self.normalize)
    #     vectorizer = TfidfVectorizer(input='filename', max_features=2000)
    #     tfidf = vectorizer.fit_transform(documents)
    #     pairwise_similarity = (tfidf * tfidf.T).toarray()
    #     return pairwise_similarity[0]

    def cosine_sim(self, text1, text2):
        vectorizer = TfidfVectorizer(input='filename', max_features=2000)
        tfidf = vectorizer.fit_transform([text1, text2])
        return round((tfidf * tfidf.T).A[0, 1], 6)

    def processone(self, file):
        filename = os.path.split(file)[-1][:-4]
        test_desc_path = os.path.join(self.OPTIONS.description, filename + ".txt")
        if os.path.exists(os.path.join(self.custom_args['Training_Set_filtered'], filename + ".csv")):
            return
        try:
            print("[+] Description analysis of " + filename)
            sim_map = {}
            flag = False
            training_set = self.custom_args['Training_Set']
            train_files = getFileList_from_txt(training_set)
            for train_file in train_files:
                train_filename = train_file
                train_desc_path = os.path.join(self.OPTIONS.description, train_filename + ".txt")
                score = self.cosine_sim(train_desc_path, test_desc_path)
                if score > self.Threshold:
                    sim_map[train_filename] = score
                    flag = True
            if flag:
                sim_lst = dict2sortedlist(sim_map)
                headings = ['Training file', 'similarity']
                writeScores(self.custom_args['Training_Set_filtered'], filename, sim_lst, headings)

        except Exception as e:
            print(e)
            return

    def start(self):
        apks = getFileList(self.custom_args['Test_Set'], ".csv")
        print("[+] Total test apks ", len(apks))
        print("[+] Saving filtered results to " + self.custom_args['Training_Set_filtered'])
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.processone, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()
