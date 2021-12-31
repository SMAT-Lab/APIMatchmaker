import re
import os
from collections import Counter
import numpy as np
import csv
csv.field_size_limit(100000000)

Presolved_path = "/home/username/APIRecommendation/Presolved_old/"
count_list = []


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


def solve(file):
    with open(file, "r") as fr:
        reader = csv.reader(fr)
        headings = next(reader)
        for line in reader:
            string = line[1].strip('\"\'[] ')
            pattern = r'(<.*?>)'
            mi = re.findall(pattern, string)
            if len(mi) < 5:
                continue
            count_list.append(len(mi))


if __name__ == '__main__':
    files = getFileList(Presolved_path, ".csv")
    for file in files:
        solve(file)

    all = 0
    num = 0
    with open("count_MI_of_MS.txt", "w") as fw:
        for item in count_list:
            fw.write(str(item) + " ")
            all += item
            num += 1

    print("avg: ", str(num), str(all / num))

    word_counts = Counter(count_list)
    # 出现频率最高的3 items
    top_three = word_counts.most_common(3)
    print(top_three)

    median = np.median(count_list)
    print("median: ", str(median))



