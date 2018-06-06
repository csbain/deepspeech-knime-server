
import time
import os
from AudioUtils import AudioUtils
from DeepSpeechImp import DeepSpeechImp
from OpenVokaturiImp import OpenVokaturiImp
from TempFileHelper import TempFileHelper
from WebRTCVADHelper import WebRTCVADHelper
import gc
import logging
import util



class SingleThreadedService:

    def print_metrics(self, seg_list):
        max_seg_length = 0
        for segment in seg_list:
            if segment.duration > max_seg_length:
                max_seg_length = segment.duration
        logging.info("Number of segments to process: "+str(len(seg_list)))
        logging.info("Longest duration of segment: "+str(max_seg_length))

    def process_audio(self, bytes, file_type, vad_aggressiveness):
        vk = OpenVokaturiImp()
        ds = DeepSpeechImp()
        temp_file_helper = TempFileHelper()
        logging.info("Preprocessing audio from "+file_type+" format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        logging.info("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file(), vad_aggressiveness)
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        self.print_metrics(seg_list)
        del web_rtcvad_helper
        del audioutil
        del bytes
        gc.collect()
        process_start_time = time.time()
        results = []
        segment_count = len(seg_list)
        count = 0
        for segment in seg_list:
            count +=1
            if count % 30 == 0:
                logging.info("restarting Deepspeech and OpenVokaturi to free up memory")
                del vk
                del ds
                gc.collect()
                vk = OpenVokaturiImp()
                ds = DeepSpeechImp()
            try:
                count = segment.order + 1
                logging.info("starting segment (processing emotion): " + str(count) + "/" + str(segment_count))
                segment.emotion = vk.analyse_audio(segment.path)
                print(segment.emotion)
                logging.info("starting segment (processing speech): " + str(count) + "/" + str(segment_count))
                start_time = time.time()
                segment.content = ds.process_audio(segment.path)
                time_taken = (time.time() - start_time)
                os.remove(segment.path)
                print(segment.content)
                logging.info("finished segment: " + str(count) + "/" + str(segment_count) + ", duration length: " + str(
                    segment.duration) + ", time taken: " + str(
                    round(time_taken, 2)) + ", duration/segment_lenght ratio: " + str(
                    round(time_taken / segment.duration, 2)))
            except Exception as e:
                logging.error("Error in segment:\n" + str(e) + "\n" + segment.get_dict_obj())
            results.append(segment.get_dict_obj())
        results_sorted = sorted(results, key=lambda k: k['order'])
        logging.info("Total time elapsed: " + util.format_time_duration(process_start_time, time.time()))
        return results_sorted


