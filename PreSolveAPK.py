# coding:utf-8
import random
import subprocess
import threadpool
from Helper.common import *
import re

tset = "/mnt/fit-Knowledgezoo/Downloads/google_apps/Apps"

class PresolveAPK:
    def __init__(self, input_path, maxjob, presolve, aapt, android_jars):
        self.input = input_path
        self.max_jobs = maxjob
        self.save_path = presolve
        self.aapt = aapt
        self.android_jars = android_jars
        self.all = 0

    def processone(self, apk):
        apkname = os.path.split(apk)[-1][:-4]
        if os.path.exists(os.path.join(self.save_path, apkname + ".csv")):
            print("[+] " + apkname + " exists!")
            return
        try:
            AAPT_CMD = self.aapt + " dump badging " + apk + "| grep package:\ name"
            output = subprocess.check_output(AAPT_CMD, shell=True, timeout=20)
        except subprocess.TimeoutExpired as exc:
            print("Command timed out: {}".format(exc))
            return
        except subprocess.CalledProcessError as e:
            output = e.output  # Output generated before error
            code = e.returncode  # Return code
            return

        aapt_output = output.decode('utf-8')
        """ EXAMPLE
        package: name='com.example.myapplication' versionCode='1' 
        versionName='1.0' compileSdkVersion='29' compileSdkVersionCodename='10'
        """

        pkg = re.findall(r"package: name='([0-9a-zA-Z.]+)'", aapt_output)
        if pkg:
            pkgname = pkg[0]
            print("[+] " + pkgname)
        else:
            return
        try:
            print("[+] PreSolving " + apkname)
            CMD = "java -Xms1024m -Xmx4096m -XX:PermSize=1024m -XX:MaxPermSize=2048m " \
                  "-XX:MaxNewSize=2048m -jar lib/APIExtractor.jar " \
                  + apk + " " + pkgname + " " + \
                  self.android_jars + " " + os.path.join(self.save_path, apkname + ".csv")
            subprocess.run(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           encoding="utf-8", timeout=30)
        except subprocess.TimeoutExpired as exc:
            print("Command timed out: {}".format(exc))
            return
        except Exception as e:
            print(e)
            return


    def start(self):
        # apks = getFileList(self.input, ".apk")
        apks = getFileList_lineage()
        random.shuffle(apks)
        self.all = len(apks)

        print("[+] Total apks ", self.all)
        print("[+] Saving results to " + self.save_path)

        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.processone, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


if __name__ == '__main__':
    input_path = "/mnt/fit-Knowledgezoo/username/APPLineage/"
    aapt = "/home/username/android-sdk-linux/build-tools/30.0.0-preview/aapt"
    andro_jar = "/home/username/android-sdk-linux/platforms"
    save_path = "/home/username/APIRecommendation/PresolvedForLineage/"

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    prosolve = PresolveAPK(input_path, 12, save_path, aapt, andro_jar)
    prosolve.start()

