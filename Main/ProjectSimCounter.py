# coding:utf-8
import math
import re

from Helper.common import *


class ProjectSimCounter:
    def __init__(self, OPTIONS, custom_args):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args

    # Compute the similarity between each testing project and all training projects
    def computeProjectSimilarity(self):
        # Read all testing project IDs in testingProjectsID
        testingProjectNames = []
        # contain similar training projects
        files = getFileList(self.custom_args['Training_Set_filtered'], ".csv")
        for file in files:
            testingPro = os.path.split(file)[-1][:-4]
            if os.path.exists(os.path.join(self.custom_args['Project_Sim'], testingPro + ".csv")):
                continue
            testingProjectNames.append(testingPro)

        trainingProjects = {}  # Map<String, Map<String, Integer>>
        trainingProjectNames = getFileList_from_txt(self.custom_args['Training_Set'])

        # Read all training projects in trainingProjects
        for trainingPro in trainingProjectNames:
            trainingProjects[trainingPro] = self.getProjectInvocations(self.OPTIONS.presolve, trainingPro)

        for testingPro in testingProjectNames:
            testingProject = self.getProjectInvocations(self.custom_args['Test_Set'], testingPro)
            trainingProjects[testingPro] = testingProject
            trainingPro_selected = self.getTrainingPro_selected(self.custom_args['Training_Set_filtered'], testingPro)
            self.computeSimilarity(testingPro, trainingProjects, trainingPro_selected)
            trainingProjects.pop(testingPro)

    def computeSimilarity(self, testingPro, projects, trainingPro_selected):
        termFrequency = self.computeTermFrequency(projects)
        testingProjectVector = {}  # {API(str): float}
        projectSimilarities = {}  # {train_project(str): float}

        print("Computing similarity between %s and all other projects" % testingPro)

        # Computes the feature vector of the testing project,
        # 	 ie. the TF-IDF for all its invocations
        terms = projects[testingPro]
        for term in terms:
            tfidf = self.computeTF_IDF(terms[term], len(projects), termFrequency[term])
            testingProjectVector[term] = tfidf

        # Compute the feature vector of all training projects in the corpus and
        # 	 store their similarity with the testing project in the similarity vector

        for trainingProject in trainingPro_selected:
            if trainingProject == testingPro:
                continue
            trainingProjectVector = {}
            terms = projects[trainingProject]
            for term in terms:
                tfidf = self.computeTF_IDF(terms[term], len(projects), termFrequency[term])
                trainingProjectVector[term] = tfidf

            similarity = self.computeCosineSimilarity(testingProjectVector, trainingProjectVector)
            projectSimilarities[trainingProject] = similarity


        # Order projects by similarity, reverse=True
        projectSimilarity_list = dict2sortedlist(projectSimilarities)

        # Saving...
        if projectSimilarity_list:
            headings = ["Training Project", "Cosine Similarity"]
            writeScores(self.custom_args['Project_Sim'], testingPro, projectSimilarity_list, headings)


    def getProjectInvocations(self, path, pro):
        terms = {}  # Map<String, Integer>
        filename = os.path.join(path, pro + ".csv")
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                string = line[1].strip('\"[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                for item in mi:
                    if item in terms:
                        terms[item] += 1
                    else:
                        terms[item] = 1
        return terms

    def getTrainingPro_selected(self, path, testPro):
        filepath = os.path.join(path, testPro + ".csv")
        if not os.path.exists(filepath):
            return None
        return getFileList_from_csv(filepath)


    def computeCosineSimilarity(self, v1, v2):
        v1_inter_v2 = list(set(v1.keys()).intersection(set(v2.keys())))
        scalar = 0.0
        norm1 = 0.0
        norm2 = 0.0
        if len(v1_inter_v2) == 0:
            return 0.0
        for f in v1.values():
            norm1 += f * f
        for f in v2.values():
            norm2 += f * f
        for item in v1_inter_v2:
            scalar += v1[item] * v2[item]

        if scalar:
            return round(scalar / math.sqrt(norm1 * norm2), 4)
        else:
            return 0.0

    def computeTermFrequency(self, projects):
        """
        :param projects: map{
        peoject_name: {api(str): time(Int)}
        }
        :return: termFrequency: map{api(str): time(Int) shown in the projects}
        """
        termFrequency = {}
        for project in projects:
            terms = projects[project]
            for term in terms:
                if term in termFrequency:
                    termFrequency[term] += 1
                else:
                    termFrequency[term] = 1
        return termFrequency

    def computeTF_IDF(self, count, total, freq):
        return 1.0 * (count * math.log(total * 1.0 / freq))

    def computeJaccardSimilarity(self, v1, v2):
        count = 0
        length = len(v1)
        for i in range(length):
            if v1[i] == 1 and v2[i] == 1:
                count += 1
        if (2 * length - count) == 0:
            return 0.0
        else:
            return (1.0 * count) / (2 * length - count)