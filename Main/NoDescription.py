import re
import threadpool
from Helper.common import *


class NoDescription:
    def __init__(self, OPTIONS, custom_args):
        self.OPTIONS = OPTIONS
        self.custom_args = custom_args
        self.max_jobs = 15
        self.trainingset = []
        self.sim_map = {}

    def processone(self, file):
        filename = os.path.split(file)[-1][:-4]
        if os.path.exists(os.path.join(self.custom_args['Training_Set_filtered'], filename + ".csv")):
            return
        try:
            headings = ['Training file', 'similarity']
            writeScores(self.custom_args['Training_Set_filtered'], filename, self.sim_lst, headings)

        except Exception as e:
            print(e)
            return

    def start(self):
        self.trainingset = getFileList_from_txt(self.custom_args['Training_Set'])
        for file in self.trainingset:
            self.sim_map[file] = 1
        self.sim_lst = dict2sortedlist(self.sim_map)
        apks = getFileList(self.custom_args['Test_Set'], ".csv")
        print("[+] Total test apks ", len(apks))
        print("[+] Saving filtered results to " + self.custom_args['Training_Set_filtered'])
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.processone, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

