# coding:utf-8
from Main.ProjectSimCounter import ProjectSimCounter
from Main.DescriptionSimCounter import DescriptionSimCounter
from Main.DescriptionSimCounter2 import DescriptionSimCounter2
from Main.DescriptionCluster import DescriptionCluster
from Main.NoDescription import NoDescription
from Main.ContextAwareRecommendation import ContextAwareRecommendation
from Main.ContextAwareRecommendation2 import ContextAwareRecommendation2
from Main.BaselineBuilder import BaselineBuilder
# from APIUsagePatternSearcher import APIUsagePatternSearcher
from Main.Evaluation import Evaluation
import time


class Runner:
    def __init__(self, OPTIONS, custom_args):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args

    def start(self):
        # start_time = time.clock()
        # print("[+] Starting ... ")

        # # (1)
        descriptionSimCounter = DescriptionSimCounter(self.OPTIONS, self.custom_args, 0)
        descriptionSimCounter.start()
        print("[+] Description Similarity done.")

        # (2)
        # noDescription = NoDescription(self.OPTIONS, self.custom_args)
        # noDescription.start()

        # Compute similarity between projects

        projectSimCounter = ProjectSimCounter(self.OPTIONS, self.custom_args)
        projectSimCounter.computeProjectSimilarity()
        print("[+] SimilarityCalculator done.")

        # Consider 10 closest projects, 6 top-closet method declarations,
        # The training projects contain at least 6 declarations

        # note here ------------------
        contextAwareRecommendation = ContextAwareRecommendation2(self.OPTIONS, self.custom_args, 10, 6, 6, 1, 0)
        contextAwareRecommendation.recommendation()
        print("[+] Recommendation engine done.")
        # note here ------------------

        #
        # end = time.clock()
        # running_time = end - start_time
        # with open("runtime.txt", "a+") as fw:
        #     fw.write(str(running_time) + "\n")
        #
        # baselinebuilder = BaselineBuilder(self.OPTIONS, self.custom_args)
        # baselinebuilder.start()
        # # Match the API usage pattern
        # apiUsagePatternSearcher = APIUsagePatternSearcher(self.OPTIONS, self.custom_args, 20)
        # apiUsagePatternSearcher.searchAPIUsagePatterns()
        # print("[+] Match API usage pattern done.")

        # note here ------------------
        print("[+] Start evaluation.")
        evaluation = Evaluation(self.OPTIONS, self.custom_args, 1)
        evaluation.start()
        evaluation = Evaluation(self.OPTIONS, self.custom_args, 5)
        evaluation.start()
        evaluation = Evaluation(self.OPTIONS, self.custom_args, 10)
        evaluation.start()
        evaluation = Evaluation(self.OPTIONS, self.custom_args, 15)
        evaluation.start()
        evaluation = Evaluation(self.OPTIONS, self.custom_args, 20)
        evaluation.start()
        print("[+] Evaluation done.")
        # note here ------------------



