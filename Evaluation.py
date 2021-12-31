import re
import sys
import os
import csv

csv.field_size_limit(100000000)


def getFileList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if filename.endswith(pick_str):
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


def getFileList2(rootDir, start_str, end_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for file in os.listdir(rootDir):
        if file.startswith(start_str) and file.endswith(end_str):
            filename = os.path.join(rootDir, file)
            filePath.append(filename)
    return filePath


class Evaluation:
    def __init__(self, OPTIONS, custom_args, n):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.n = n

    def start(self):
        testingProjectNames = []
        files = getFileList(self.custom_args['Training_Set_filtered'], ".csv")
        for file in files:
            testingProjectNames.append(os.path.split(file)[-1][:-4])
        for testPro in testingProjectNames:
            GT_set = self.getGroundTruthInvocations_set(self.custom_args['GroundTruth_PATH'], testPro, self.n)
            pre_lst = self.getPrediction_lst(self.custom_args['RECOMMENDATION_PATH'], testPro, self.n)
            if len(GT_set) < self.n or len(pre_lst) < self.n:
                continue
            intersections = GT_set.intersection(set(pre_lst))
            precision = 1.0 * len(intersections) / self.n
            recall = 1.0 * len(intersections) / len(GT_set)
            self.record_acc("evaluationhalfhalf_", testPro, precision, recall)

    def record_acc(self, outputpath, testPro, precision, recall):
        s = self.custom_args['Test_Set'].split('/')
        dataset = list(filter(None, s))[-2]
        with open(outputpath + str(self.n) + "_" + dataset + ".csv", "a+", newline="") as fw:
            writer = csv.writer(fw)
            writer.writerow([testPro, round(precision, 6), round(recall, 6)])

    # use set() to do the evaluation, cuz many mi duplications
    def getGroundTruthInvocations_set(self, path, testingPro, n):
        gtInvocations = set()
        filename = os.path.join(path, testingPro + ".csv")
        if not os.path.exists(filename):
            return None
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                # md = line[0].strip('\"[] ')
                string = line[1].strip('\"\'[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                gtInvocations = gtInvocations.union(set(mi))
        return gtInvocations

    def getPrediction_lst(self, path, testingPro, n):
        PreInvocations = []
        filename = os.path.join(path, testingPro + ".csv")
        if not os.path.exists(filename):
            return None
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                # line_num start from 2
                if reader.line_num <= n + 1:
                    mi = line[0].strip('\"\'[] ')
                    PreInvocations.append(mi)
        return PreInvocations

    def getBaseline_lst(self, path, testingPro, n):
        base_set = []
        filename = os.path.join(path, testingPro + ".txt")
        if not os.path.exists(filename):
            return None
        count = 0
        with open(filename, "r") as fr:
            line = fr.readline().strip()
            while line and count < n:
                base_set.append(line)
                count += 1
                line = fr.readline().strip()
        return base_set


def count_precision(files):
    all = 0.0
    num = 0
    for file in files:
        with open(file, "r") as fr:
            reader = csv.reader(fr)
            for line in reader:
                score = float(line[1])
                all += score
                num += 1
    print("precision: " + str(all / (num + 0.01)))


def count_recall(files):
    all = 0.0
    num = 0
    for file in files:
        with open(file, "r") as fr:
            reader = csv.reader(fr)
            for line in reader:
                score = float(line[2])
                all += score
                num += 1
    print("recall: " + str(all / (num + 0.01)))


def count_successrate(files):
    valid = 0
    num = 0
    for file in files:
        with open(file, "r") as fr:
            reader = csv.reader(fr)
            for line in reader:
                score = float(line[1])
                if score:
                    valid += 1
                num += 1
    print("valid samples: " + str(num))
    print("success rate: " + str(valid / (num + 0.01)))


if __name__ == '__main__':
    baseline_or_not = int(sys.argv[1])  # 1 or 0
    topnum = str(sys.argv[2])
    if baseline_or_not:
        start_s = "baseline_evaluation"
    else:
        start_s = "evaluation"
    start_s = start_s + topnum + "_"
    print(start_s)

    path = os.getcwd()
    print(path)
    files = getFileList2(path, start_s, ".csv")
    print(files)

    count_precision(files)
    count_recall(files)
    count_successrate(files)
