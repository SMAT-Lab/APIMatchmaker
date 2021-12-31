# coding:utf-8
import re
import numpy as np
from Main.ProjectSimCounter import ProjectSimCounter
from Helper.common import *


class ContextAwareRecommendation2:
    testingMIs = {}
    listOfProjects = []
    listOfMethodInvocations = []
    numOfSlices = 0
    numOfRows = 0
    numOfCols = 0

    def __init__(self, OPTIONS, custom_args, numOfNeighbours, sizeofMi, min_lines, P_S, D_S):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.numOfNeighbours = numOfNeighbours
        self.sizeofMi = sizeofMi
        self.min_lines = min_lines
        self.projectSIm = P_S
        self.DescSim = D_S


    def clear_pre(self):
        self.listOfProjects = []
        self.listOfMethodInvocations = []
        self.numOfSlices = 0
        self.numOfRows = 0
        self.numOfCols = 0

    # Recommend new invocations for every testing project using the
    # collaborative-filtering technique

    def recommendation(self):

        # load sdk files
        minsdk = "minSdkVersion.txt"
        targetsdk = "targetSdkVersion.txt"
        csvfile = "android_api_lifetime.txt"
        sdkset = load_file(csvfile)
        minsdkset = load_sdks(minsdk)
        targetsdkset = load_sdks(targetsdk)

        testingProjects = self.getTestingProjectNames()
        for testingPro in testingProjects:
            self.clear_pre()
            if os.path.exists(os.path.join(self.custom_args['RECOMMENDATION_PATH'], testingPro + ".csv")):
                continue
            recommendations = {}  # {str: float}
            descsimScores = self.getDescsimScores(self.custom_args['Training_Set_filtered'], testingPro)
            simi_path = self.custom_args['Project_Sim']
            simScores = self.getSimilarityScores(simi_path, testingPro, self.numOfNeighbours)
            matrix = self.buildUserItemContextMatrix(testingPro)

            # The testingMethodVector represents the invocations made from the testing method
            testingMethodVector = matrix[self.numOfSlices - 1][self.numOfRows - 1]
            mdSimScores = {}  # {str: float}

            # Compute the jaccard similarity between the testingMethod and every other method
            # and store the results in mdSimScores
            for i in range(self.numOfSlices - 1):
                for j in range(self.numOfRows):
                    otherMethodVector = matrix[i][j]
                    simCalculator = ProjectSimCounter(self.OPTIONS, self.custom_args)
                    sim = simCalculator.computeJaccardSimilarity(testingMethodVector, otherMethodVector)
                    key = str(i) + "#" + str(j)
                    mdSimScores[key] = sim

            # Sort the results
            simSortedList = dict2sortedlist(mdSimScores)

            # Compute the top-3 most similar methods
            top3Sim = simSortedList[:self.sizeofMi]

            # Initial
            ratings = [0.0] * (self.numOfCols - 1)

            # For every '?' cell (-1.0), compute a rating
            for k in range(self.numOfCols):
                if matrix[self.numOfSlices - 1][self.numOfRows - 1][k] == -1:
                    totalSim = 0.0

                    # Iterate over the top-3 most similar methods
                    for item in top3Sim:
                        key = item[0]
                        parts = key.split("#")
                        slice = int(parts[0])
                        row = int(parts[1])
                        # Compute the average rating of the method declaration
                        avgMDRating = 0.0
                        for m in range(self.numOfCols):
                            avgMDRating += matrix[slice][row][m]
                        avgMDRating /= self.numOfCols

                        project = self.listOfProjects[slice]
                        projectSim = simScores[project]
                        descSim = descsimScores[project]

                        # Project similarity * the close method's val (1 or 0)
                        R_val = (projectSim * self.projectSIm + descSim * self.DescSim) * matrix[slice][row][k]
                        methodSim = item[1]  # top-3 method Jaccard sim
                        totalSim += methodSim
                        ratings[k] += (R_val - avgMDRating) * methodSim

                    if totalSim:
                        ratings[k] /= totalSim
                    activeMDrating = 0.8
                    ratings[k] += activeMDrating
                    methodInvocation = self.listOfMethodInvocations[k]
                    recommendations[methodInvocation] = ratings[k]

            recSortedList = dict2sortedlist(recommendations)
            headings = ["Method Invocation", "Rating"]

            filtered_sdk_lst = []
            for tmplst in recSortedList:
                methodInvocation = tmplst[0]
                if testingPro not in minsdkset or testingPro not in targetsdkset:
                    continue
                min_sdk_ = minsdkset[testingPro]
                target_sdk_ = targetsdkset[testingPro]
                if methodInvocation in sdkset:
                    supportsdks = sdkset[methodInvocation]
                    if min_sdk_ >= supportsdks[0] and target_sdk_ <= supportsdks[-1] and 30 in supportsdks:
                        filtered_sdk_lst.append(tmplst)
                        if len(filtered_sdk_lst) == 20:
                            break

            writeScores(self.custom_args['RECOMMENDATION_PATH'], testingPro, filtered_sdk_lst, headings)

        return self.testingMIs


    # Build a 3-D user-item-context ratings matrix
    def buildUserItemContextMatrix(self, testingPro):
        # list
        simProjects = self.getMostSimilarProjects(testingPro, self.numOfNeighbours)
        allProjects = {}
        listOfPRs = []
        allMDs = set()
        allMIs = set()

        for project in simProjects:
            # The last parameter means at least x lines (each line means a method)
            tmpMIs = self.getProjectDetailsFromTrainingProjects(self.OPTIONS.presolve, project, self.min_lines)
            if not tmpMIs:
                continue

            allMDs = allMDs.union(tmpMIs.keys())
            for mis in tmpMIs.values():
                allMIs = allMIs.union(mis)

            allProjects[project] = tmpMIs
            listOfPRs.append(project)

        # The slice for the testing project is located at the end of the matrix
        listOfPRs.append(testingPro)

        # For evaluation !!!
        # Read the corresponding groundtruth file, set(md: [mis...])
        # Keep in order with list, normally, only one item in "groundTruthMIs"
        # This step is to get the testingMD
        groundTruthMIs = self.getGroundTruthInvocations(self.custom_args['GroundTruth_PATH'], testingPro)

        testingMD = ""  # md needs to be recommended
        for item in groundTruthMIs:
            testingMD = item

        # Add the testing project, excluding ground-truth method invocations
        # Get all the MIs from the testing project
        tmpMIs = self.getTestingProjectDetails(self.custom_args['Test_Set'], testingPro, testingMD)
        allMDs = allMDs.union(tmpMIs.keys())

        for item in tmpMIs.values():
            allMIs = allMIs.union(item)

        tmpMISet = self.testingMIs[testingMD]  # all or existing ?

        # Add testing data to the list of invocations/projects
        tmpMIs[testingMD] = tmpMISet  # {md: set()}
        allProjects[testingPro] = tmpMIs

        # Convert to an ordered list of all method declarations to make sure
        # that the testing method declaration locates at the end of the list
        listOfMDs = list(allMDs)
        if testingMD in listOfMDs:
            listOfMDs.remove(testingMD)
        listOfMDs.append(testingMD)

        # Convert to an ordered list of all method invocations to make sure
        # that all testing method invocations locate at the end of the list
        listOfMIs = list(allMIs)
        for testingMI in tmpMISet:
            if testingMI in listOfMIs:
                listOfMIs.remove(testingMI)

        for testingMI in tmpMISet:
            listOfMIs.append(testingMI)

        self.numOfSlices = len(listOfPRs)
        self.numOfRows = len(listOfMDs)
        self.numOfCols = len(listOfMIs)

        # Populate all cells in the user-item-context ratings matrix using 1s and 0s
        matrix = np.zeros([self.numOfSlices, self.numOfRows, self.numOfCols], dtype=np.int)

        for i in range(self.numOfSlices - 1):
            currentPro = listOfPRs[i]
            myMDs = allProjects[currentPro]
            for j in range(self.numOfRows):
                currentMD = listOfMDs[j]
                if currentMD in myMDs:
                    myMIs = myMDs[currentMD]
                    for k in range(self.numOfCols):
                        currentMI = listOfMIs[k]
                        if currentMI in myMIs:
                            matrix[i][j][k] = 1

        # This is the testing project, ie. the last slice of the 3-D matrix
        myMDs = allProjects[testingPro]
        for j in range(self.numOfRows - 1):
            currentMD = listOfMDs[j]
            if currentMD in myMDs:
                myMIs = myMDs[currentMD]
                for k in range(self.numOfCols):
                    currentMI = listOfMIs[k]
                    if currentMI in myMIs:
                        matrix[self.numOfSlices - 1][j][k] = 1

        # The method needs to be tested
        currentMD = listOfMDs[self.numOfRows - 1]
        myMIs = myMDs[currentMD]
        for k in range(self.numOfCols):
            currentMI = listOfMIs[k]
            if currentMI in myMIs:
                matrix[self.numOfSlices - 1][self.numOfRows - 1][k] = 1
            else:
                matrix[self.numOfSlices - 1][self.numOfRows - 1][k] = -1

        for l in listOfPRs:
            self.listOfProjects.append(l)

        for l in listOfMIs:
            self.listOfMethodInvocations.append(l)

        return matrix

    def getDescsimScores(self, desc_sim, testingPro):
        Desc_scores = {}
        filename = os.path.join(desc_sim, testingPro + ".csv")
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                Desc_scores[line[0]] = float(line[1])
        return Desc_scores


    # Get all method invocations that do not belong to the ground-truth data
    def getTestingProjectDetails(self, src, testingPro, testingMD):
        methodInvocations = {}  # {str: set(str)}
        filename = os.path.join(src, testingPro + ".csv")
        tmp = set()
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                md = line[0].strip('\"\'[] ')
                string = line[1].strip('\"\'[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                mi = set(mi)

                # get the testing method invocations
                if testingMD == md:
                    tmp = tmp.union(mi)
                # other method invocations, we get them all
                else:
                    if md in methodInvocations:
                        methodInvocations[md] = methodInvocations[md].union(mi)
                    else:
                        methodInvocations[md] = mi

        self.testingMIs[testingMD] = tmp
        return methodInvocations


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


    def getMostSimilarProjects(self, filename, size):
        projects = []
        count = 0

        simi_path = self.custom_args['Project_Sim']

        eva_score_path = os.path.join(simi_path, filename + ".csv")
        if not os.path.exists(eva_score_path):
            return None
        with open(eva_score_path, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                if count < size:
                    projects.append(line[0])
                    count += 1
        return projects


    def getProjectDetailsFromTrainingProjects(self, path, project, size):
        methodInvocations = {}
        filename = os.path.join(path, project + ".csv")
        if row_count(filename) < size:
            return None
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                md = line[0].strip('\"\'[] ')
                string = line[1].strip('\"\'[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                mi = set(mi)

                if md in methodInvocations:
                    methodInvocations[md] = methodInvocations[md].union(mi)
                else:
                    methodInvocations[md] = mi
        return methodInvocations

    def getSimilarityScores(self, dir, testingPro, size):
        projects = {}  # {str: float}
        count = 0
        filename = os.path.join(dir, testingPro + ".csv")
        with open(filename, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                URI = line[0].strip()
                score = float(line[1].strip())
                projects[URI] = score
                count += 1
                if count == size:
                    break

        return projects

    def getTestingProjectNames(self):
        names = []
        files = getFileList(self.custom_args['Training_Set_filtered'], ".csv")
        for file in files:
            names.append(os.path.split(file)[-1][:-4])
        return names
