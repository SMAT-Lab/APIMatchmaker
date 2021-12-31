import math
import re
from Helper.common import *

class DatasetGenerator:
    # Remove the project containing fewer than 6 method invocations
    def __init__(self, k, input_path, Dataset_path, Splitdata_path, check_dir, half_or_all, num_for_test):
        self.k = k
        self.Dataset_path = Dataset_path
        self.check_mk_dir(Dataset_path)
        self.splitdata_path = Splitdata_path
        self.check_mk_dir(Splitdata_path)
        self.data = input_path
        self.half_or_all = half_or_all
        self.num_for_test = num_for_test
        self.check_dir = check_dir

    def start(self):
        self.SplitDatat()

    def SplitDatat(self):
        files = getFileList(self.data, ".csv")
        all_files = []
        for file in files:
            filename = os.path.split(file)[-1][:-4]
            if os.path.exists(os.path.join(self.check_dir, filename + ".txt")):
                all_files.append(file)
        all = len(all_files)
        print(str(all) + " files in total.")
        n = int(math.ceil(all * 1.0 / self.k))
        list_of_groups = [all_files[i: i + n] for i in range(0, all, n)]
        for i in range(self.k):
            self.recordGroups(list_of_groups)
            Dir_name = self.Dataset_path + "dataset_" + str(i) + "/"
            self.check_mk_dir(Dir_name)
            Training_file = Dir_name + "TrainingSet.txt"
            Test_dir = Dir_name + "TestSet/"
            self.check_mk_dir(Test_dir)
            GT_dir = Dir_name + "GroundTruth/"
            self.check_mk_dir(GT_dir)
            sub_files = list_of_groups[i]
            for file in sub_files:
                if self.half_or_all == "all":
                    self.split_test_GT(file, Test_dir, GT_dir)
                else:
                    self.split_test_GT_half(file, Test_dir, GT_dir)
            for file in all_files:
                if file in sub_files:
                    continue
                self.cp_to_trainingset(file, Training_file)

    def split_test_GT(self, file, Test_dir, GT_dir):
        filename = os.path.split(file)[-1]
        last_line_number = row_count(file)
        if last_line_number > 10000:
            return
        with open(file, "r") as fr:
            reader = csv.reader(fr)
            # filter less than 6
            headings = next(reader)
            print("[+] Line num: " + str(last_line_number))
            if last_line_number < 7:
                return
            test_file = os.path.join(Test_dir, filename)
            GT_file = os.path.join(GT_dir, filename)
            fw = open(test_file, "w")
            writer = csv.writer(fw)
            writer.writerow(headings)
            for row in reader:
                if last_line_number == reader.line_num:
                    print("[+] Processing the last line...")
                    string = row[1].strip('\"[] ')
                    pattern = r'(<.*?>)'
                    mi = re.findall(pattern, string)
                    if self.num_for_test == "1":
                        stop_index = 1
                    elif self.num_for_test == "4":
                        stop_index = 4
                    for_test = mi[:stop_index]
                    for_GT = mi[stop_index:]
                    with open(GT_file, "w") as fwg:
                        writerg = csv.writer(fwg)
                        writerg.writerow(headings)
                        writerg.writerow([row[0], for_GT])
                else:
                    writer.writerow(row)
            writer.writerow([row[0], for_test])
            fw.close()

    def split_test_GT_half(self, file, Test_dir, GT_dir):
        filename = os.path.split(file)[-1]
        last_line_number = row_count(file)
        if last_line_number > 10000:
            return
        with open(file, "r") as fr:
            reader = csv.reader(fr)
            # filter less than 6
            headings = next(reader)
            print("[+] Line num: " + str(last_line_number))
            if last_line_number < 7:
                return
            test_file = os.path.join(Test_dir, filename)
            GT_file = os.path.join(GT_dir, filename)
            fw = open(test_file, "w")
            writer = csv.writer(fw)
            writer.writerow(headings)
            if last_line_number % 2 == 0:
                half_line = (last_line_number / 2) + 1
            else:
                half_line = (last_line_number + 1) / 2 + 1
            for row in reader:
                if reader.line_num < half_line:
                    writer.writerow(row)
                elif reader.line_num == half_line:
                    print("[+] Processing the half line...")
                    string = row[1].strip('\"[] ')
                    pattern = r'(<.*?>)'
                    mi = re.findall(pattern, string)
                    if self.num_for_test == "1":
                        stop_index = 1
                    elif self.num_for_test == "4":
                        stop_index = 4
                    for_test = mi[:stop_index]
                    for_GT = mi[stop_index:]
                    with open(GT_file, "w") as fwg:
                        writerg = csv.writer(fwg)
                        writerg.writerow(headings)
                        writerg.writerow([row[0], for_GT])
                    break
            writer.writerow([row[0], for_test])
            fw.close()

    def recordGroups(self, list_of_groups):
        for i in range(self.k):
            record_file = os.path.join(self.splitdata_path, str(i) + ".txt")
            with open(record_file, "w") as fw:
                for item in list_of_groups[i]:
                    fw.write(item + "\n")

    def check_mk_dir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

    def cp_to_trainingset(self, file, Training_file):
        # filter less than 6
        line_count = row_count(file)
        if line_count < 6 or line_count > 10000:
            return
        filename = os.path.split(file)[-1][:-4]
        with open(Training_file, "a+") as fw:
            fw.write(filename + "\n")

def sortedDictValues1(adict):
    keys1 = sorted(adict.keys())
    return [[key, adict[key]] for key in keys1]

def rank(original, new):
    check_and_mk_dir(new)
    files = getFileList(original, ".csv")
    for file in files:
        file_map = {}
        filename = os.path.split(file)[-1][:-4]
        file_new = os.path.join(new, filename + ".csv")
        if os.path.exists(file_new):
            continue
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
                file_map[line[0]] = mi
            lst = sortedDictValues1(file_map)
            for item in lst:
                writer.writerow(item)
            fw.close()


if __name__ == '__main__':
    all_or_half = ["all", "half"]
    left_num = ["1", "4"]
    check_dir = "/home/username/APIRecommendation/Description_presolved/"
    Input_path = "/home/username/APIRecommendation/Presolved_filtered/"

    New_Input_path = "/home/username/APIRecommendation/Presolved_ranked/"

    rank(Input_path, New_Input_path)
    Dataset_path = "datasets_ranked_half_4/"
    Splitdata_path = Dataset_path + "splitdata/"
    datasetGenerator = DatasetGenerator(10, New_Input_path, Dataset_path, Splitdata_path, check_dir, "half", "4")
    datasetGenerator.start()
