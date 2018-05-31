
import concurrent.futures
import time
import os
from AudioUtils import AudioUtils
from DeepSpeechImp import DeepSpeechImp
from OpenVokaturiImp import OpenVokaturiImp
from TempFileHelper import TempFileHelper
from WebRTCVADHelper import WebRTCVADHelper
import gc
import resource
import multiprocessing
import time
import signal

# https://pymotw.com/2/resource/
#  https://docs.python.org/3.6/library/multiprocessing.html
#  https://sebastianraschka.com/Articles/2014_multiprocessing.html
# http://stackabuse.com/parallel-processing-in-python/
# http://oz123.github.io/writings/2015-02-25-Simple-Multiprocessing-Task-Queue-in-Python/index.html
# http://www.davekuhlman.org/python_multiprocessing_01.html
# https://www.journaldev.com/15631/python-multiprocessing-example
# https://pymotw.com/2/multiprocessing/communication.html
# https://docs.python.org/3/library/resource.html
class Consumer(multiprocessing.Process):


    def __init__(self, task_queue, result_queue, segment_count, memlimit):
        multiprocessing.Process.__init__(self)

        self.segment_count = segment_count
        self.task_queue = task_queue
        self.result_queue = result_queue
        signal.signal(signal.SIGXCPU, resource_exit)
        # resource.setrlimit(resource.RLIMIT_CPU, (1, hard))
        soft, hard = resource.getrlimit(resource.RLIMIT_VMEM)
        resource.setrlimit(resource.RLIMIT_VMEM, (memlimit, hard))

    def resource_exit(n, stack):
        # print('EXPIRED :', time.ctime())
        raise SystemExit('(time ran out)')



    def run(self):
        self.vk = OpenVokaturiImp()
        self.ds = DeepSpeechImp()
        proc_name = self.name
        while True:
            next_segment = self.task_queue.get()
            if next_segment is None:
                # Poison pill means shutdown
                print('%s: Exiting' % proc_name)
                self.task_queue.task_done()
                break
            result = self.process_segment(next_segment)
            self.task_queue.task_done()
            self.result_queue.put(result)
        return


    def process_segment(self, segment):
        try:
            print("starting segment (processing emotion): " + str(segment.order) + "/" + str(self.segment_count))
            segment.emotion = self.vk.analyse_audio(segment.path)
            print(segment.emotion)
            print("starting segment (processing speech): " + str(segment.order) + "/" + str(self.segment_count))
            start_time = time.time()
            segment.content = self.ds.process_audio(segment.path)
            time_taken = (time.time() - start_time)
            os.remove(segment.path)
            print(segment.content)
            print(
                "finished segment: " + str(segment.order) + "/" + str(self.segment_count) + ", duration length: " + str(
                    segment.duration) + ", time taken: " + str(
                    round(time_taken, 2)) + ", duration/segment_lenght ratio: " + str(
                    round(time_taken / segment.duration, 2)))
            return segment.get_dict_obj()
        except Exception as e:
            print("Error in segment:")
            print(str(e))
            print(segment.get_dict_obj())
            return {}



class Service2:

    def print_metrics(self, seg_list):
        max_seg_length = 0
        for segment in seg_list:
            if segment.duration > max_seg_length:
                max_seg_length = segment.duration
        print("Number of segments to process: " + str(len(seg_list)))
        print("Longest duration of segment: " + str(max_seg_length))

    def process_audio(self, bytes, file_type):
        temp_file_helper = TempFileHelper()
        print("Preprocessing audio from "+file_type+" format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        print("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        self.print_metrics(seg_list)
        web_rtcvad_helper = None
        audioutil = None
        bytes = None
        gc.collect()
        print("processing single threaded")
        start_time = time.time()
        results = []
        num_jobs = len(seg_list)

        count = 0
        tasks_queue = multiprocessing.JoinableQueue()
        results_queue = multiprocessing.Queue()
        num_consumers = multiprocessing.cpu_count()
        # num_consumers = 1
        consumers = [Consumer(tasks_queue, results_queue, len(seg_list))
                     for i in range(num_consumers)]

        for w in consumers:
            w.start()
            # Enqueue jobs
        for segment in seg_list:
            tasks_queue.put(segment)
        # Add a poison pill for each consumer
        for i in range(num_consumers):
            tasks_queue.put(None)

        tasks_queue.join()
        while num_jobs:
            results.append(results_queue.get())
            num_jobs -= 1

        results_sorted = sorted(results, key=lambda k: k['order'])
        time_taken = (time.time() - start_time)
        print("--- %s seconds ---\n\n" % time_taken)
        return results_sorted


if __name__ == "__main__":
    import sys
    import re

    # file = sys.argv[1]
    file = "alice.mp3"
    extensions = re.findall(r'\.([^.]+)', file)
    service = Service2()

    with open(file, "rb") as in_file:

        results = service.process_audio(in_file.read(),extensions[0])
        print(results)

