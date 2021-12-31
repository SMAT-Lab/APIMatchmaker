# coding:utf-8
import hashlib
import os
import csv
import re

csv.field_size_limit(100000000)
import pandas as pd

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


def getFileList_lineage():
    CSV_FOLDER = "/home/username/myazdownload/analyzecsv/csv_folder/"
    APPFOLDER = "/mnt/fit-Knowledgezoo/username/APPLineage/"
    CHECK_PATH = "/mnt/fit-Knowledgezoo-vault/vault/apks/"
    save = "lineagelist.txt"
    fileslist = []
    if os.path.exists(save):
        with open(save, "r") as fr:
            lines = fr.readlines()
            for line in lines:
                fileslist.append(line.strip())
        return fileslist

    count = 0
    MAX = 1000
    files = getFileList(CSV_FOLDER, ".csv")
    for file in files:
        tmp = []
        if count > MAX:
            return fileslist
        line_count = row_count(file)
        if line_count < 7:
            continue
        with open(file, 'r') as fr:
            df = pd.read_csv(fr, header=0)
            for i in range(len(df)):
                SHA256 = df.iloc[i]['sha256']
                apkpath = os.path.join(CHECK_PATH, SHA256 + ".apk")
                apkpath2 = os.path.join(APPFOLDER, SHA256 + ".apk")
                if os.path.exists(apkpath):
                    tmp.append(apkpath)
                elif os.path.exists(apkpath2):
                    tmp.append(apkpath2)
        if len(tmp) >= 6:
            fileslist.extend(tmp)
            count += len(tmp)
    with open(save, "w") as fw:
        for item in fileslist:
            fw.write(item + "\n")
    return fileslist


def getFileList_from_txt(txtfile):
    files = []
    with open(txtfile, "r") as fr:
        for line in fr.readlines():
            files.append(line.strip())
    return files


def getFileList_from_csv(csvfile):
    files = []
    with open(csvfile, "r") as fr:
        reader = csv.reader(fr)
        headings = next(reader)
        for line in reader:
            files.append(line[0].strip())
    return files


def get_sha256(s):
    m = hashlib.sha256()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def dict2sortedlist(dic: dict):
    lst = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    return lst


def writeScores(saveDir, project_name, score_list, headings):
    with open(os.path.join(saveDir, project_name + ".csv"), "w", newline="") as fw:
        writer = csv.writer(fw)
        writer.writerow(headings)
        writer.writerows(score_list)

def load_device(filename):
    devices = {}
    with open(filename, 'r') as fr:
        reader = csv.reader(fr)
        for line in reader:
            if line[0] == "level":
                continue
            api = line[1]
            devices[api] = 1
    return devices

def load_file(filename):
    res = {}
    with open(filename, "r") as fr:
        lines = fr.readlines()
        for line in lines:
            if not line:
                continue
            s = line.split(">:")
            api_sig = s[0].strip() + ">"
            sdks = re.split("]:", s[1].strip("<>"))
            tmp = sdks[0].strip("[] ").split(",")
            new = []
            for item in tmp:
                new.append(int(item))
            res[api_sig] = new
    return res


def load_all_apis(path):
    all = {}
    files = getFileList(path, ".csv")
    for file in files:
        with open(file, "r") as fr:
            reader = csv.reader(fr)
            headings = next(reader)
            for line in reader:
                string = line[1].strip('\"[] ')
                pattern = r'(<.*?>)'
                mi = re.findall(pattern, string)
                for item in mi:
                    all[item] = 1

    return list(all.keys())

def load_sdks(minsdk1):
    minsdkset = {}
    with open(minsdk1, "r") as fr:
        lines = fr.readlines()
        for line in lines:
            if line:
                sha256 = line.split(" ")[0]
                v = line.split(" ")[1]
                minsdkset[sha256] = int(v)
    return minsdkset


def row_count(filename):
    with open(filename) as in_file:
        return sum(1 for _ in in_file)


def check_and_mk_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

