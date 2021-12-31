import sys
import argparse
import time

from Runner import Runner
from Helper.common import *

Presolved_PATH = "/data/sdc/username/APIRecommendation/Presolved_filtered/"
Description_PATH = "/data/sdc/username/APIRecommendation/Description_presolved/"
T_dir = "datasets/dataset_0/"


def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-i", "--input", default="", help="Path of the input APKs.")
    parser.add_argument("-pre", "--presolve", default=Presolved_PATH, help="Path of the presolved temporary files.")
    parser.add_argument("-d", "--description", default=Description_PATH, help="Path of the description of APKs.")
    parser.add_argument("-data", "--dataset", default=T_dir, help="Root dir of the dataset.")

    parser.add_argument("-a", "--android_jars", default="/home/username/android-sdk-linux/platforms", help="Path of the dir of android jars.")
    parser.add_argument("-p", "--aapt", default="aapt", help="Path of aapt.")

    parser.add_argument("-m", "--maxjob", type=int, default=10, help="Max job of threadpools.")
    options = parser.parse_args(args)
    return options


if __name__ == '__main__':

    OPTIONS = getOptions()

    if not OPTIONS.dataset.endswith("/"):
        OPTIONS.dataset += "/"
    T_dir = OPTIONS.dataset

    OUTPUT_PATH = T_dir + "UsagePattern/"
    RECOMMENDATION_PATH = T_dir + "Recommendation/"
    Project_Sim = T_dir + "ProjectSim/"
    Training_Set = T_dir + "TrainingSet.txt"
    Training_Set_filtered = T_dir + "TrainingSet_filtered/"
    Test_Set = T_dir + "TestSet/"
    GroundTruth_PATH = T_dir + "GroundTruth/"
    BaseLine_PATH = T_dir + "BaseLine/"
    custom_args = {
        'OUTPUT_PATH': OUTPUT_PATH,
        'RECOMMENDATION_PATH': RECOMMENDATION_PATH,
        'Project_Sim': Project_Sim,
        'Training_Set_filtered': Training_Set_filtered,
        'Training_Set': Training_Set,
        'Test_Set': Test_Set,
        'GroundTruth_PATH': GroundTruth_PATH,
        'BaseLine_PATH': BaseLine_PATH
    }

    if OPTIONS.android_jars.endswith("/"):
        OPTIONS.android_jars = OPTIONS.android_jars[:-1]

    for item in custom_args:
        if item not in ['Training_Set']:
            check_and_mk_dir(custom_args[item])

    Runner(OPTIONS, custom_args).start()
