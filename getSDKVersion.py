# apt dump badging *.apk|grep Version
import os
import re
import subprocess

def getFileList(rootDir, pickstr):
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pickstr in filename:
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath

def getSDK(apkpath):
    try:
        AAPT_CMD = "aapt dump badging " + apkpath + "| grep Version"
        # sdkVersion:'19'
        # targetSdkVersion:'28'
        output = subprocess.check_output(AAPT_CMD, shell=True, timeout=20)
    except subprocess.TimeoutExpired as exc:
        print("Command timed out: {}".format(exc))
        return
    except subprocess.CalledProcessError as e:
        output = e.output  # Output generated before error
        code = e.returncode  # Return code
        return

    aapt_output = output.decode('utf-8')

    min = re.findall(r"sdkVersion:'([0-9]+)'", aapt_output)
    if min:
        minSdk = min[0]
    else:
        return

    target = re.findall(r"targetSdkVersion:'([0-9]+)'", aapt_output)
    if target:
        targetSdk = target[0]
    else:
        return

    print(minSdk, targetSdk)
    return minSdk, targetSdk


if __name__ == "__main__":
    min1 = {}
    target = {}
    APKPATH = "/data/sdc/username/APK2020"
    files = getFileList(APKPATH, ".apk")
    print(len(files))

    for file in files:
        try:
            minSdk, targetSdk = getSDK(file)
            if minSdk and targetSdk:
                sha256 = os.path.split(file)[-1][:-4]
                min1[sha256] = minSdk
                target[sha256] = target
        except Exception as e:
            print(file)
            print(e)
            continue

    print(len(min1))
    with open("/data/sdc/username/APIMatchmaker/minSdkVersion.txt", "w") as fw:
        for sha256 in min1:
            fw.write(sha256 + " ")
            fw.write(str(min1[sha256]))
            fw.write("\n")



