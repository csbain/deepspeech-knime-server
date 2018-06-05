
import time
import os
from AudioUtils import AudioUtils
from DeepSpeechImp import DeepSpeechImp
from OpenVokaturiImp import OpenVokaturiImp
from TempFileHelper import TempFileHelper
from WebRTCVADHelper import WebRTCVADHelper
import gc
import multiprocessing

class Service4:

    def print_metrics(self, seg_list):
        max_seg_length = 0
        for segment in seg_list:
            if segment.duration > max_seg_length:
                max_seg_length = segment.duration
        print("Number of segments to process: "+str(len(seg_list)))
        print("Longest duration of segment: "+str(max_seg_length))

    def process_segment_list_worker(self, seg_list, total_count, results_queue):
        vk = OpenVokaturiImp()
        ds = DeepSpeechImp()
        results = []
        segment_count = len(seg_list)
        for segment in seg_list:
            count +=1
            try:
                count = segment.order + 1
                print("starting segment (processing emotion): " + str(count) + "/" + str(segment_count))
                segment.emotion = vk.analyse_audio(segment.path)
                print(segment.emotion)
                print("starting segment (processing speech): " + str(count) + "/" + str(segment_count))
                start_time = time.time()
                segment.content = ds.process_audio(segment.path)
                time_taken = (time.time() - start_time)
                os.remove(segment.path)
                print(segment.content)
                print("finished segment: " + str(count) + "/" + str(segment_count) + ", duration length: " + str(
                    segment.duration) + ", time taken: " + str(
                    round(time_taken, 2)) + ", duration/segment_lenght ratio: " + str(
                    round(time_taken / segment.duration, 2)))
            except Exception as e:
                print("Error in segment:")
                print(str(e))
                print(segment.get_dict_obj())
            results.append(segment.get_dict_obj())
        del vk
        del ds
        gc.collect()
        results_queue.put(results)

    def process_audio(self, bytes, file_type):

        temp_file_helper = TempFileHelper()
        print("Preprocessing audio from "+file_type+" format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        print("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        self.print_metrics(seg_list)
        total_count = len(seg_list)
        del web_rtcvad_helper
        del audioutil
        del bytes
        gc.collect()
        print("processing single threaded")
        start_time = time.time()
        num_consumers = multiprocessing.cpu_count()
        chunked_seg_list = list(self.chunks(seg_list, num_consumers))

        result_queue = multiprocessing.Queue()
        jobs = []
        for seg_list_chunk in chunked_seg_list:
            p = multiprocessing.Process(target=self.process_segment_list_worker, args=(seg_list_chunk,total_count, result_queue))
            jobs.append(p)
            p.start()
        for p in jobs:
            p.join()
        results = []
        for p in jobs:
            results += result_queue.get()
        result_queue.close()
        time_taken = (time.time() - start_time)
        print("--- %s seconds ---\n\n" % time_taken)

        return results


    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]