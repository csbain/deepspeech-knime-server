import concurrent.futures
import time
from AudioUtils import AudioUtils
from DeepSpeechImp import DeepSpeechImp
from OpenVokaturiImp import OpenVokaturiImp
from TempFileHelper import TempFileHelper
from WebRTCVADHelper import WebRTCVADHelper


class Service:
    
    vk = OpenVokaturiImp()
    ds = DeepSpeechImp()
    segment_count = 0

    def process_segment(self, segment):
        try:
            
            print("starting segment (processing emotion): " + str(segment.order)+"/"+str(self.segment_count))
            segment.emotion = self.vk.analyse_audio(segment.path)
            print(segment.emotion)
            print("starting segment (processing speech): " + str(segment.order)+"/"+str(self.segment_count))
            start_time = time.time()
            segment.content = self.ds.process_audio(segment.path)
            time_taken = (time.time() - start_time)
            print(segment.content)
            print("finished segment: " + str(segment.order)+"/"+str(self.segment_count) + ", duration length: "+ str(segment.duration) +", time taken: " + str(round(time_taken, 2)) +", duration/segment_lenght ratio: " + str(round(time_taken/segment.duration, 2)))
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
        print("Number of segments to process: "+str(len(seg_list)))
        print("Longest duration of segment: "+str(max_seg_length))



    def process_audio_singlethreaded(self, bytes, file_type):
        temp_file_helper = TempFileHelper()
        print("Preprocessing audio from "+file_type+" format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        print("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        self.print_metrics(seg_list)
        del web_rtcvad_helper, audioutil, bytes
        print("processing single threaded")
        start_time = time.time()
        results = []
        self.segment_count = len(seg_list)
        for segment in seg_list:
            results.append(self.process_segment(segment))

        time_taken = (time.time() - start_time)
        print("--- %s seconds ---\n\n" % time_taken)

        return results

    def process_audio_multithreaded(self, bytes, file_type):
        temp_file_helper = TempFileHelper()
        print("Preprocessing audio from "+file_type+" format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        print("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        self.print_metrics(seg_list)
        del web_rtcvad_helper, audioutil, bytes
        print("processing multithreaded")
        start_time = time.time()
        results = []
        self.segment_count = len(seg_list)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            to_do = []
            for segment in seg_list:
                future = executor.submit(self.process_segment, segment)
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
