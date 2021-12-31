# coding:utf-8
import re
from Helper.common import *

class APIUsagePatternSearcher:

    def __init__(self, OPTIONS, custom_args, numOfRecs):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.numOfRecs = numOfRecs

    def searchAPIUsagePatterns(self):
        # Collect in allProjects the method invocations for every training project
        allProjects = {}  # Map<String, Map<String, Set<String>>>

        # ？？？only the most similar projects are considered
        trainingProjects = getFileList_from_txt(self.custom_args['Training_Set'])
        testingProjects = self.getProjectNames(self.custom_args['Training_Set_filtered'])

        for trainingProject in trainingProjects:
            # projectMIs - Map<String, Set<String>> projectMIs
            projectMIs = self.getProjectDetails(self.OPTIONS.presolve, trainingProject)
            allProjects[trainingProject] = projectMIs

        #  For every testingPro, collect the Jaccard distance
        #  between the recommendations and the actual invocations
        for testingPro in testingProjects:
            results = {}  # Map<String, Float>
            # ordered lists
            recommendations = []
            testingInvocations = self.getTestingInvocations(self.custom_args['Test_Set'], testingPro)

            # Searching API usage pattern for testingPro
            # add also the testing invocation(s)
            for invocation in testingInvocations:
                recommendations.append(invocation)

            recommendations.extend(self.readRecommendationFile(self.custom_args['RECOMMENDATION_PATH'], testingPro))

            for project in allProjects:
                methodInvocations = allProjects[project]

                for declaration in methodInvocations:
                    invocations = methodInvocations[declaration]
                    allMIs = set()

                    # Md in training projects
                    s_train = len(invocations)
                    # Recoomendations in test project
                    s_test = len(recommendations)

                    short_len = min(s_train, s_test)
                    for i in range(short_len):
                        allMIs.add(recommendations[i])

                    size1 = len(invocations.intersection(allMIs))
                    size2 = len(invocations.union(allMIs))
                    if size1:
                        jaccard = (1.0 * size1) / size2
                        results[project + "#" + declaration] = jaccard

            jaccard_sim_list = dict2sortedlist(results)
            numOfRecs = self.numOfRecs
            if len(jaccard_sim_list) > numOfRecs:
                jaccard_sim_list = jaccard_sim_list[:numOfRecs]
            headings = ["Project#Declaration", "Jaccard Similarity"]
            writeScores(self.custom_args['OUTPUT_PATH'], testingPro, jaccard_sim_list, headings)


    def readRecommendationFile(self, path, project):
        ret = []
        filename = os.path.join(path, project + ".csv")
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                mi = line[0]
                ret.append(mi)
        return ret


    def getTestingInvocations(self, path, project):
        ret = []
        filename = os.path.join(path, project + ".csv")
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                md = line[0].strip('\"[] ')
                string = line[1].strip('\"[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                ret = mi
        return ret


    def getProjectDetails(self, path, project):
        # return a Map<String, Set<String>>
        methodInvocations = {}
        filename = os.path.join(path, project + ".csv")

        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                md = line[0].strip('\"[] ')
                string = line[1].strip('\"[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                mi = set(mi)

                if md in methodInvocations:
                    methodInvocations[md] = methodInvocations[md].union(mi)
                else:
                    methodInvocations[md] = mi

        return methodInvocations

    def getProjectNames(self, path):
        names = []
        files = getFileList(path, ".csv")
        for file in files:
            names.append(os.path.split(file)[-1][:-4])
        return names






