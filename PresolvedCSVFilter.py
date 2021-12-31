import re
import string
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import threadpool
from Helper.common import *

class PresolvedCSVFilter:
    def __init__(self, input_path, description_path, new_description_path, save_path, MD_min, MI_min, max_job):
        self.input_path = input_path
        self.save_path = save_path
        self.description_path = description_path
        self.new_description_path = new_description_path
        self.MD_min = MD_min
        self.MI_min = MI_min
        self.max_jobs = max_job
        self.english_stopwords = stopwords.words("english")

    def processone(self, file):
        filename = os.path.split(file)[-1][:-4]
        file_new = os.path.join(save_path, filename + ".csv")
        if os.path.exists(file_new):
            return
        with open(file, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            fw = open(file_new, "w")
            writer = csv.writer(fw)
            writer.writerow(headings)
            for line in reader:
                line_new = []
                string = line[1].strip('\"[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                new_mi, count = self.count_MIs(mi)  # count = len(mi) without dup
                if 15 <= count <= 30:
                    line_new.append(line[0])
                    line_new.append(new_mi)
                    line_new.append(reader.line_num)
                    writer.writerow(line_new)
            fw.close()
            if row_count(file_new) < 6:
                os.remove(file_new)
                return

        desc_file = os.path.join(self.description_path, filename + ".txt")
        if not os.path.exists(desc_file):
            os.remove(file_new)
            return
        if not self.check_lang(desc_file):
            os.remove(file_new)
            return
        new_desc = self.normalize(desc_file)
        new_desc_path = os.path.join(self.new_description_path, filename + ".txt")
        with open(new_desc_path, "w") as fw:
            fw.write(" ".join(new_desc))


    def check_lang(self, file):
        count = 0
        with open(file, "r") as fr:
            content = fr.read()
            for char in content:
                if ord(char) > 128:
                    count += 1
        # Non English char / all < 0.1, keep; otherwise, remove
        if 1.0 * count / len(content) < 0.1:
            return True
        else:
            return False

    # lemmatizer
    def lemmatizer(self, tokens):
        wordnet_lemmatizer = WordNetLemmatizer()
        return [wordnet_lemmatizer.lemmatize(item) for item in tokens]

    # stemming
    def stem_tokens(self, tokens):
        stemmer = PorterStemmer()
        return [stemmer.stem(item) for item in tokens]

    '''remove punctuation, lowercase, stem'''

    def judge_pure_english(self, keyword):
        return all(ord(c) < 128 for c in keyword)

    def normalize(self, file):
        with open(file, "r") as fr:
            text = fr.read()
        words_cut = word_tokenize(text)
        words_lower = [i.lower() for i in words_cut if len(i) > 3]
        words_clear = []
        for i in words_lower:
            if not self.judge_pure_english(i):
                continue
            if i not in self.english_stopwords and i not in string.punctuation:
                i1 = re.sub('[^a-zA-Z]', '', i)
                words_clear.append(i1)
        return self.stem_tokens(words_clear)

    def count_MIs(self, lst):
        # remove dup? yes
        new_lst = []
        count = 0
        for item in lst:
            if item not in new_lst:
                new_lst.append(item)
                count += 1 
        return new_lst, count


    def start(self):
        csvs = getFileList(self.input_path, ".csv")
        self.all = len(csvs)
        print("[+] Total csvs ", self.all)
        print("[+] Saving results to " + self.save_path)

        args = [(apk) for apk in csvs]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.processone, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


if __name__ == '__main__':
    input_path = "/home/username/APIRecommendation/Presolved/"
    description_path = "/home/username/APIRecommendation/Description_fromGP/"
    # new_description_path = "/home/username/APIRecommendation/Description_presolved/"
    new_description_path = "/home/username/APIRecommendation/Description_lemmatized/"
    save_path = "/home/username/APIRecommendation/Presolved_lemmatized/"
    check_and_mk_dir(save_path)
    check_and_mk_dir(new_description_path)
    PresolvedCSVFilter(input_path, description_path, new_description_path, save_path, 6, 15, 15).start()
