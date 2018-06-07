import gc
import logging
import math
import multiprocessing
import os
import datetime
import time
import util
from audio_utils import AudioUtils
from deep_speech_imp import DeepSpeechImp
from open_vokaturi_imp import OpenVokaturiImp
from temp_file_helper import TempFileHelper
from web_rtc_vad_helper import WebRTCVADHelper


class MultiProcessorService:

    def print_metrics(self, seg_list):
        max_seg_length = 0
        for segment in seg_list:
            if segment.duration > max_seg_length:
                max_seg_length = segment.duration
        logging.info("Number of segments to process: " + str(len(seg_list)))
        logging.info("Longest duration of segment: " + str(max_seg_length))

    def process_segment_list_worker(self, seg_list, total_count, results_queue):
        vk = OpenVokaturiImp()
        ds = DeepSpeechImp()
        results = []
        for segment in seg_list:
            try:
                segment.start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                count = segment.order + 1
                logging.info("starting segment (processing emotion): " + str(count) + "/" + str(total_count))
                segment.emotion = vk.analyse_audio(segment.path)
                logging.debug(segment.emotion)
                logging.info("starting segment (processing speech): " + str(count) + "/" + str(total_count))
                start_time = time.time()
                segment.content = ds.process_audio(segment.path)
                time_taken = (time.time() - start_time)
                os.remove(segment.path)
                logging.debug(segment.content)
                logging.info("finished segment: " + str(count) + "/" + str(total_count) + ", duration length: " + str(
                    segment.duration) + ", time taken: " + str(
                    round(time_taken, 2)) + ", duration/segment_lenght ratio: " + str(
                    round(time_taken / segment.duration, 2)))
                segment.end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                logging.error("Error in segment:\n" + str(e) + "\n" + str(segment.get_dict_obj()))
            results.append(segment.get_dict_obj())
        del vk
        del ds
        gc.collect()
        results_queue.put(results)

    def process_audio(self, bytes, file_type, vad_aggressiveness):

        temp_file_helper = TempFileHelper()
        logging.info("Preprocessing audio from " + file_type + " format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        logging.info("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file(), vad_aggressiveness)
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        self.print_metrics(seg_list)
        total_count = len(seg_list)
        del web_rtcvad_helper
        del audioutil
        del bytes
        gc.collect()
        process_start_time = time.time()
        num_consumers = multiprocessing.cpu_count()
        chunked_seg_list = list(self.chunks(seg_list, math.ceil(len(seg_list) / num_consumers)))
        result_queue = multiprocessing.Queue()
        jobs = []
        for seg_list_chunk in chunked_seg_list:
            p = multiprocessing.Process(target=self.process_segment_list_worker,
                                        args=(seg_list_chunk, total_count, result_queue))
            jobs.append(p)
            p.start()
        for p in jobs:
            p.join()
        results = []
        for p in jobs:
            results += result_queue.get()
        result_queue.close()
        results_sorted = sorted(results, key=lambda k: k['order'])

        logging.info("Total time elapsed: " + util.format_time_duration(process_start_time, time.time()))
        return results_sorted

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]
