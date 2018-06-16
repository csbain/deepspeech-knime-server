import gc
import logging
import os
import datetime
import time
import util
import audio_utils
from deep_speech_imp import DeepSpeechImp
from open_vokaturi_imp import OpenVokaturiImp
from web_rtc_vad_helper import WebRTCVADHelper
import concurrent.futures

class ASRService:

    def process_audio(self, file_bytes, file_type, vad_aggressiveness, processes):
        logging.info("Preprocessing audio from " + file_type + " format")
        logging.info("Breaking down audio into smaller chunks")
        webrtcvadhelper = WebRTCVADHelper()
        seg_list = webrtcvadhelper.get_sr_segment_list(audio_utils.process_audio_dsp(file_bytes, file_type), vad_aggressiveness)
        self.print_metrics(seg_list)
        total_count = len(seg_list)
        del file_bytes
        gc.collect()
        process_start_time = time.time()
        num_consumers = processes
        if num_consumers > 1:
            num_consumers = num_consumers - 1 # allow one spare process for main thread
        results = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_consumers) as executor:
            to_do = []
            for segment in seg_list:
                future = executor.submit(self.process_segment, segment, total_count)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                result_temp = {"order": -1}
                try:
                    result_temp = future.result(timeout=360)
                except concurrent.futures.TimeoutError:
                    print("this took too long...")
                    future.interrupt()
                except Exception as e:
                    print('error: ' + str(e))
                finally:
                    results.append(result_temp)

        results_sorted = sorted(results, key=lambda k: k['order'])
        logging.info("Total time elapsed: " + util.format_time_duration(process_start_time, time.time()))

        return results_sorted




    def print_metrics(self, seg_list):
        max_seg_length = 0
        for segment in seg_list:
            if segment.duration > max_seg_length:
                max_seg_length = segment.duration
        logging.info("Number of segments to process: " + str(len(seg_list)))
        logging.info("Longest duration of segment: " + str(max_seg_length))

    def process_segment(self, segment, total_count):
        try:
            vk = OpenVokaturiImp()
            ds = DeepSpeechImp()
            segment.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        except Exception as e:
            logging.error("Error in segment:\n" + str(e) + "\n" + str(segment.get_dict_obj()))
            segment.exception = str(e)
        finally:
            segment.end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            del vk
            del ds
            gc.collect()
        return segment.get_dict_obj()


