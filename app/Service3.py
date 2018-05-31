import concurrent.futures
import multiprocessing
import time
import os
from AudioUtils import AudioUtils
from DeepSpeechImp import DeepSpeechImp
from OpenVokaturiImp import OpenVokaturiImp
from TempFileHelper import TempFileHelper
from WebRTCVADHelper import WebRTCVADHelper
import gc


class Service3:
    segment_count = 0


    def run_queue_watcher(self):
        vk = OpenVokaturiImp()
        ds = DeepSpeechImp()
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


    def print_metrics(self, seg_list):
        max_seg_length = 0
        for segment in seg_list:
            if segment.duration > max_seg_length:
                max_seg_length = segment.duration
        print("Number of segments to process: " + str(len(seg_list)))
        print("Longest duration of segment: " + str(max_seg_length))

    #
    # def process_audio_singlethreaded(self, bytes, file_type):
    #
    #     temp_file_helper = TempFileHelper()
    #     print("Preprocessing audio from "+file_type+" format")
    #     audioutil = AudioUtils(temp_file_helper, bytes, file_type)
    #     print("Breaking down audio into smaller chunks")
    #     web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
    #     seg_list = web_rtcvad_helper.get_sr_segment_list()
    #     self.print_metrics(seg_list)
    #     web_rtcvad_helper = None
    #     audioutil = None
    #     bytes = None
    #     gc.collect()
    #     print("processing single threaded")
    #     start_time = time.time()
    #     results = []
    #     self.segment_count = len(seg_list)
    #     count = 0
    #     for segment in seg_list:
    #         count +=1
    #         if count % 20 == 0:
    #             print("restarting Deepspeech and OpenVokaturi to free up memory")
    #             self.vk = None
    #             self.ds = None
    #             gc.collect()
    #             self.vk = OpenVokaturiImp()
    #             self.ds = DeepSpeechImp()
    #
    #         results.append(self.process_segment(segment))
    #
    #     time_taken = (time.time() - start_time)
    #     print("--- %s seconds ---\n\n" % time_taken)
    #
    #     return results
    #
    # def process_audio_multithreaded(self, bytes, file_type):
    #     temp_file_helper = TempFileHelper()
    #     print("Preprocessing audio from "+file_type+" format")
    #     audioutil = AudioUtils(temp_file_helper, bytes, file_type)
    #     print("Breaking down audio into smaller chunks")
    #     web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
    #     seg_list = web_rtcvad_helper.get_sr_segment_list()
    #     self.print_metrics(seg_list)
    #     web_rtcvad_helper = None
    #     audioutil = None
    #     bytes = None
    #     gc.collect()
    #     print("processing multithreaded")
    #     start_time = time.time()
    #     results = []
    #     self.segment_count = len(seg_list)
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    #         to_do = []
    #         for segment in seg_list:
    #             future = executor.submit(self.process_segment, segment)
    #             to_do.append(future)
    #         for future in concurrent.futures.as_completed(to_do):
    #             result_temp = {}
    #             try:
    #                 result_temp = future.result(timeout=60)
    #                 results.append(result_temp)
    #             except concurrent.futures.TimeoutError:
    #                 print("this took too long...")
    #                 future.interrupt()
    #             except Exception as e:
    #                 print('error: ' + str(e))
    #             finally:
    #                 results.append(result_temp)
    #
    #     time_taken = (time.time() - start_time)
    #     print("--- %s seconds ---\n\n" % time_taken)
    #
    #     results_sorted = sorted(results, key=lambda k: k['order'])
    #
    #     return results_sorted

    def process_audio_multiprocessor(self, bytes, file_type):
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














        temp_file_helper = TempFileHelper()
        print("Preprocessing audio from " + file_type + " format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        print("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        self.print_metrics(seg_list)
        web_rtcvad_helper = None
        audioutil = None
        bytes = None
        gc.collect()
        print("processing multithreaded")
        start_time = time.time()
        results = []
        self.segment_count = len(seg_list)
        num_consumers = multiprocessing.cpu_count()
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_consumers) as executor:
            to_do = []
            for segment in seg_list:
                future = executor.submit(self.process_segment, segment, ds, vk, len(seg_list))
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                result_temp = {}
                try:
                    result_temp = future.result(timeout=60)
                    results.append(result_temp)
                except concurrent.futures.TimeoutError:
                    print("this took too long...")
                    future.interrupt()
                except Exception as e:
                    print('error: ' + str(e))
                finally:
                    results.append(result_temp)

        time_taken = (time.time() - start_time)
        print("--- %s seconds ---\n\n" % time_taken)

        results_sorted = sorted(results, key=lambda k: k['order'])

        return results_sorted


if __name__ == "__main__":
    import sys
    import re

    # file = sys.argv[1]
    file = "alice.mp3"
    extensions = re.findall(r'\.([^.]+)', file)
    service = Service()

    with open(file, "rb") as in_file:
        results = service.process_audio_multiprocessor(in_file.read(), extensions[0])
        print(results)


