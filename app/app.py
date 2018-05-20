from AudioUtils import AudioUtils
from WebRTCVADHelper import WebRTCVADHelper
from TempFileHelper import TempFileHelper
from DeepSpeechImp import DeepSpeechImp
from OpenVokaturiImp import OpenVokaturiImp


import concurrent.futures
import time
import json

ds = DeepSpeechImp()
vk = OpenVokaturiImp()


def process_segment(segment):
    try:

        print("starting "+str(segment.order))
        segment.emotion = vk.analyse_audio(segment.path)
        print("middle " + str(segment.order))
        segment.content = ds.process_audio(segment.path)

        print("finished " + str(segment.order))
        return segment.get_dict_obj()
    except Exception:
        return {}


def main():
    temp_file_helper = TempFileHelper()

    bytes = None
    print("reading file")
    # with open("wip/obama_interview.wav", "rb") as in_file:
    #     bytes = in_file.read()
    with open("wip/obama_interview.wav", "rb") as in_file:
        bytes = in_file.read()

    print("starting process")
    audioutil = AudioUtils(temp_file_helper, bytes, "wav")
    web_rtcvad_helper = WebRTCVADHelper(temp_file_helper, audioutil.get_processed_file())


    seg_list = web_rtcvad_helper.get_sr_segment_list()
    del web_rtcvad_helper, audioutil, bytes
    print("processing file multithreaded")
    # exit()
    start_time = time.time()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        to_do = []
        for segment in seg_list:
            future = executor.submit(process_segment, segment)
            to_do.append(future)
        for future in concurrent.futures.as_completed(to_do):
            try:
                results.append(future.result())
            except Exception as e:
                print('error: '+str(e))


        # for result in executor.map(process_segment, seg_list):
        #     results.append(result)

        # futures = executor.submit(process_segment, seg_list)
        #
        #
        # futures = [executor.submit(downloader, url) for url in urls]
        #
        # last_result = {}
        # try:
        #     for result in executor.map(process_segment, seg_list):
        #         try:
        #             last_result = result
        #             results.append(result)
        #         except Exception as ex:
        #             results.append({})
        #             print(ex)
        # except Exception as ex:
        #     print(last_result)
        #     print(ex)


    time_taken = (time.time() - start_time)
    print("--- %s seconds ---\n\n" % time_taken)
    jsonObj = json.dumps(results)
    # print(jsonObj)
    with open("/home/chris/multithreaded4_result.txt", "w") as text_file:
        text_file.write("--- %s seconds ---" % time_taken)
        text_file.write(jsonObj)

    print("ended processing file multithreaded")
    print("\n\n--------------------------------------\n\n")
    exit()
    print("processing file singlethreaded")
    ds = DeepSpeechImp()
    vk = OpenVokaturiImp()
    start_time = time.time()
    results = []
    for seg in seg_list:
        results.append(process_segment(seg))
    time_taken = (time.time() - start_time)
    print("--- %s seconds ---" % time_taken)
    jsonObj = json.dumps(results)
    # print(jsonObj)
    with open("/home/chris/singlethreaded_result.txt", "w") as text_file:
        text_file.write("--- %s seconds ---\n\n" % time_taken)
        text_file.write(jsonObj)
    print("ended processing file singlethreaded")

    # for seg in seg_list:
    #     print(ds.process_audio(seg.path))
    #     print(vk.analyse_audio(seg.path))
    #     break
    # print("writing file")
    # audioutil.save_output_to_wav("wip.wav")





if __name__ == '__main__':
   main()

