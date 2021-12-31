import sys
import csv
csv.field_size_limit(sys.maxsize)
import os
import hashlib

ANDROID_SDK = "/home/username/android-sdk-linux/"
# JADX_TOOL_PATH = "jadx"
JADX_TOOL_PATH = "/home/username/jadx/build/jadx/bin/jadx"

XMLPATH = "GATOR2XML"
APKPATH = "/mnt/fit-Knowledgezoo/username/APK_with_DESC"
CSVPATH = "XML2CSV"
JADXPATH = "JADXOUTPUT"
DEFAULT_MAX_JOB = 5


def getFileList(rootDir, pickstr):
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pickstr in filename:
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


def check_and_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()
