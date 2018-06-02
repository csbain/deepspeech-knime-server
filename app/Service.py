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

class Service:
    def process_segment(self, segments_chunk, total_count):

        vk = OpenVokaturiImp()
        ds = DeepSpeechImp()
        finished_segments = []
        for segment in segments_chunk:

            try:
                print("starting segment (processing emotion): " + str(segment.order)+"/"+str(total_count))
                segment.emotion = vk.analyse_audio(segment.path)
                print(segment.emotion)
                print("starting segment (processing speech): " + str(segment.order)+"/"+str(total_count))
                start_time = time.time()
                segment.content = ds.process_audio(segment.path)
                time_taken = (time.time() - start_time)
                os.remove(segment.path)
                print(segment.content)
                print("finished segment: " + str(segment.order)+"/"+str(total_count) + ", duration length: "+ str(segment.duration) +", time taken: " + str(round(time_taken, 2)) +", duration/segment_lenght ratio: " + str(round(time_taken/segment.duration, 2)))

            except Exception as e:
                print("Error in segment:")
                print(str(e))
                print(segment.get_dict_obj())
            finally:
                finished_segments.append(segment.get_dict_obj())
        del vk
        del ds
        gc.collect()
        # return segment.get_dict_obj()
        return finished_segments


    def print_metrics(self, seg_list):
        max_seg_length = 0
        for segment in seg_list:
            if segment.duration > max_seg_length:
                max_seg_length = segment.duration
        print("Number of segments to process: "+str(len(seg_list)))
        print("Longest duration of segment: "+str(max_seg_length))


    def process_audio_multiprocessor(self, bytes, file_type):
        temp_file_helper = TempFileHelper()
        print("Preprocessing audio from "+file_type+" format")
        audioutil = AudioUtils(temp_file_helper, bytes, file_type)
        print("Breaking down audio into smaller chunks")
        web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())
        seg_list = web_rtcvad_helper.get_sr_segment_list()
        chunked_seg_list = list(self.chunks(seg_list, 5))


        self.print_metrics(seg_list)
        web_rtcvad_helper = None
        audioutil = None
        bytes = None
        gc.collect()
        print("processing multithreaded")
        start_time = time.time()
        results = []
        segment_count = len(seg_list)
        num_consumers = multiprocessing.cpu_count()
        # num_consumers = 2
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_consumers) as executor:

            to_do = []
            for segments_chunk in chunked_seg_list:
                future = executor.submit(self.process_segment, segments_chunk, segment_count)
                to_do.append(future)
            for future in concurrent.futures.as_completed(to_do):
                result_temp = {"order":-1}
                try:
                    result_temp = future.result(timeout=120)
                except concurrent.futures.TimeoutError:
                    print("this took too long...")
                    future.interrupt()

                except Exception as e:
                    print('error: ' + str(e))
                finally:
                    results += result_temp

        time_taken = (time.time() - start_time)
        print("--- %s seconds ---\n\n" % time_taken)

        results_sorted = sorted(results, key=lambda k: k['order'])

        return results_sorted

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]



if __name__ == "__main__":
    import sys
    import re

    # file = sys.argv[1]
    file = "alice.mp3"
    extensions = re.findall(r'\.([^.]+)', file)
    service = Service()

    with open(file, "rb") as in_file:

        results = service.process_audio_multiprocessor(in_file.read(),extensions[0])
        print(results)


