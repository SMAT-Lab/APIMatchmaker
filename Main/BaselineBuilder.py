import pickle
import re
from Helper.common import *

class BaselineBuilder:
    def __init__(self, OPTIONS, custom_args):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.pairsavingpath = os.path.join(self.custom_args['BaseLine_PATH'], "baseline_pairs.pkl")

    def predict_with_baseline(self, savepath, num):
        testingProjects = self.getTestingProjectNames()
        for testingPro in testingProjects:
            answer = self.predict_one(testingPro, num)
            # print(answer)
            self.saveAnswer(answer, savepath, testingPro)

    def predict_one(self, testingPro, num):
        groundTruthMIs = self.getGroundTruthInvocations(self.custom_args['GroundTruth_PATH'], testingPro)

        testingMD = ""  # md needs to be recommended
        for item in groundTruthMIs:
            testingMD = item

        lastmi = self.getTheLastLineofTestingProject(self.custom_args['Test_Set'], testingPro, testingMD)
        answer = []
        for i in range(num):
            if lastmi in self.pairs:
                rankedlst = self.pairs[lastmi]
                flag = 0
                for item in rankedlst:
                    if item[0] not in answer:
                        answer.append(item[0])
                        lastmi = item[0]
                        flag = 1
                        break
                if flag == 0:
                    answer.append("<null>")
                    lastmi = "<null>"
            else:
                answer.append("<null>")
                lastmi = "<null>"
        return answer

    # Get all method invocations that do not belong to the ground-truth data
    def getTheLastLineofTestingProject(self, src, testingPro, testingMD):
        filename = os.path.join(src, testingPro + ".csv")
        lastmi = ""
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                md = line[0].strip('\"\'[] ')
                if md == testingMD:
                    string = line[1].strip('\"\'[] ')
                    pattern = r'(<.*?>)'
                    mi = re.findall(pattern, string)
                    lastmi = mi[-1]
        return lastmi

    def getGroundTruthInvocations(self, path, testingPro):
        gtInvocations = {}
        filename = os.path.join(path, testingPro + ".csv")
        if not os.path.exists(filename):
            return None
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                md = line[0].strip('\"\'[] ')
                string = line[1].strip('\"\'[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                # per md per line
                if md in gtInvocations:
                    gtInvocations[md].extend(mi)
                else:
                    gtInvocations[md] = mi

        return gtInvocations

    def getTestingProjectNames(self):
        names = []
        files = getFileList(self.custom_args['Training_Set_filtered'], ".csv")
        for file in files:
            names.append(os.path.split(file)[-1][:-4])
        return names

    def buildMap(self, input_txt, detail_dir):
        if os.path.exists(self.pairsavingpath):
            return
        self.map = {}
        files = getFileList_from_txt(input_txt)
        for file in files:
            tmp = self.getDetailsFromTrainingProjects(detail_dir, file)
            for md in tmp:
                milst = tmp[md]
                milst2 = milst[1:]
                milst1 = milst[:-1]
                for i in range(len(milst) - 1):
                    pre = milst1[i]
                    next = milst2[i]
                    if pre in self.map:
                        if next in self.map[pre]:
                            self.map[pre][next] += 1
                        else:
                            self.map[pre][next] = 1
                    else:
                        self.map[pre] = {}
                        self.map[pre][next] = 1

    def buildPairs(self):
        self.pairs = {}
        if os.path.exists(self.pairsavingpath):
            self.loadpairs(self.pairsavingpath)
        else:
            for item in self.map:
                # tmp is a dict
                tmp = self.map[item]
                # remove it self
                if item in tmp:
                    tmp[item] = 0
                lst = dict2sortedlist(tmp)
                self.pairs[item] = lst

    def getDetailsFromTrainingProjects(self, save_dair, file):
        filepath = os.path.join(save_dair, file + ".csv")
        methodInvocations = {}
        with open(filepath, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                md = line[0].strip('\"\'[] ')
                string = line[1].strip('\"\'[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                if md in methodInvocations:
                    methodInvocations[md].extend(mi)
                else:
                    methodInvocations[md] = mi
        return methodInvocations

    def loadpairs(self, input):
        with open(input, "rb") as f:
            self.pairs = pickle.load(f)

    def savepairs(self, output):
        with open(output, "wb") as f:
            pickle.dump(self.pairs, f)

    def saveAnswer(self, answer, path, testingPro):
        filepath = os.path.join(path, testingPro + ".txt")
        with open(filepath, "w") as fw:
            for item in answer:
                fw.write(item + "\n")

    def start(self):
        self.buildMap(self.custom_args['Training_Set'], self.OPTIONS.presolve)
        self.buildPairs()
        self.savepairs(self.pairsavingpath)
        self.predict_with_baseline(self.custom_args['BaseLine_PATH'], 20)

