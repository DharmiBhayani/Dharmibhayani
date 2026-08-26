import time



class LatencyTracker:


    def __init__(self):

        self.start_time = None



    def start(self):

        self.start_time = time.time()



    def end(self):

        if self.start_time:

            return time.time() - self.start_time


        return 0