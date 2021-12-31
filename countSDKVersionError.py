import csv
import os
import re
import subprocess

minsdk = "/data/sdc/username/APIMatchmaker/minSdkVersion.txt"
targetsdk = "/data/sdc/username/APIMatchmaker/targetSdkVersion.txt"
csvfile = "/data/sdc/username/android_api_lifetime.txt"
devicepath = "/data/sdc/username/device_specific_apis.csv"
examplepath = "/data/sdc/username/recommendation/APIhalf4/datasets_10_6_half_4/dataset_0/Recommendation"
allapis = "/data/sdc/username/APIRecommendation/Presolved_filtered/"


def getFileList(rootDir, pickstr):
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pickstr in filename:
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


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
    lst = []
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
            lst.append(api_sig)
    return res, lst


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


def read_recommended_apis(file):
    apis = []
    with open(file, "r") as fr:
        reader = csv.reader(fr)
        for line in reader:
            if "<" in line[0]:
                apis.append(line[0])
    return apis


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


if __name__ == "__main__":
    devices = load_device(devicepath)
    print(len(devices))
    sdkset, apiset = load_file(csvfile)
    print(len(sdkset))
    minsdkset = load_sdks(minsdk)
    print(len(minsdkset))
    all_api_set = load_all_apis(allapis)
    print(len(all_api_set))

    # all_reco_apis = {}
    # files = getFileList(examplepath, ".csv")
    # for file in files:
    #     sha256 = os.path.split(file)[-1][:-4]
    #     apis = read_recommended_apis(file)
    #     all_reco_apis[sha256] = apis

    all_reco_apis = {}
    files = getFileList(examplepath, ".csv")
    for file in files:
        sha256 = os.path.split(file)[-1][:-4]
        all_reco_apis[sha256] = []

    all_sdk_error = []
    all_device_error = []
    all_sdk_error_count = 0
    all_device_error_count = 0
    all_error_count = 0
    all_count = 0
    for sha256 in all_reco_apis:
        if sha256 not in minsdkset:
            continue
        min_sdk_ = minsdkset[sha256]

        api_recommendation = all_api_set
        for api in api_recommendation:

            if api in devices:
                all_count += 1
                all_error_count += 1
                all_device_error_count += 1
                all_device_error.append(api + "|" + sha256 + "|device")

            if api in sdkset:
                supportsdks = sdkset[api]
                all_count += 1

                if min_sdk_ < supportsdks[0]:
                    all_sdk_error.append(api + "|" + sha256 + "|" + str(min_sdk_))
                    all_error_count += 1
                    all_sdk_error_count += 1
                    continue

                if 30 not in supportsdks:
                    all_sdk_error.append(api + "|" + sha256 + "|30")
                    all_error_count += 1
                    all_sdk_error_count += 1
                    continue

    print(all_count, all_sdk_error, all_device_error, all_error_count)

    with open("save_error_api.txt", "w") as fw:
        for item in all_sdk_error:
            fw.write(item)
            fw.write("\n")
        for item in all_device_error:
            fw.write(item)
            fw.write("\n")








