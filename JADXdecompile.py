import os
import subprocess
import threadpool

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

APKPATH = "/data/sdc/username/APK2020"
CSVPATH = "/data/sdc/username/APIRecommendation/Presolved_filtered"
JADXPATH = "/data/sdc/username/JADXOUTPUT"
DEFAULT_MAX_JOB = 5

class JADXdecompile:
    def compile_one(self, apk):
        if not os.path.exists(apk):
            return False
        apkname = os.path.split(apk)[-1][:-4]
        if os.path.exists(JADXPATH + "/" + apkname):
            return True
        try:
            print("[+] Decompiling " + apkname)
            # CMD = "~/jadx/build/jadx/bin/jadx -d " + JADXPATH + "/" + apkname + " " + apk
            CMD = "jadx -d " + JADXPATH + "/" + apkname + " " + apk
            out_bytes = subprocess.check_output(CMD, shell=True, timeout=100)
        except subprocess.TimeoutExpired as exc:
            print("Command timed out: {}".format(exc))
            return True
        except subprocess.CalledProcessError as e:
            out_bytes = e.output  # Output generated before error
            code = e.returncode  # Return code
            return False
        # out_text = out_bytes.decode('utf-8')
        return True

    def start(self):
        print("[+] Decompiling with JADX...")
        check_and_mkdir(JADXPATH)
        apk_tmp = getFileList(APKPATH, ".apk")
        csvs = getFileList(CSVPATH, ".csv")
        apks = []
        for apk in apk_tmp:
            apkname = os.path.split(apk)[-1][:-4]
            csv_name = os.path.join(CSVPATH, apkname + ".csv")
            if csv_name in csvs:
                apks.append(apk)
        print("[+] Decompiling " + str(len(apks)) + " files...")

        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(DEFAULT_MAX_JOB)
        requests = threadpool.makeRequests(self.compile_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

