import concurrent.futures
import time
from AudioUtils import AudioUtils
from DeepSpeechImp import DeepSpeechImp
from OpenVokaturiImp import OpenVokaturiImp
from TempFileHelper import TempFileHelper
from WebRTCVADHelper import WebRTCVADHelper


class Service:
    ds = DeepSpeechImp()
    vk = OpenVokaturiImp()

    def process_segment(self, segment):
        try:
            print("starting segment (processing emotion): " + str(segment.order))
            segment.emotion = self.vk.analyse_audio(segment.path)
            print("starting segment (processing speech): " + str(segment.order))
            segment.content = self.ds.process_audio(segment.path)
            print("finished segment: " + str(segment.order))
            return segment.get_dict_obj()
        except Exception as e:
            print("Error in segment: " + str(segment.order)) + "\n\n" + str(e)
            return {}

    def process_audio(self, bytes, file_type):
        temp_file_helper = TempFileHelper()
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        del web_rtcvad_helper, audioutil, bytes
        print("processing")
        start_time = time.time()
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            to_do = []
            for segment in seg_list:
                future = executor.submit(self.process_segment, segment)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                try:
                    results.append(future.result())
                except Exception as e:
                    print('error: ' + str(e))

        time_taken = (time.time() - start_time)
        print("--- %s seconds ---\n\n" % time_taken)

        results_sorted = sorted(results, key=lambda k: k['order'])

        return results_sorted
