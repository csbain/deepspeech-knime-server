import threading
import metrics_logger
from multi_processor_service import MultiProcessorService
from single_threaded_service import SingleThreadedService
import logging
import json
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')


def get_file_bytes(filename):
    with open(filename, "rb") as in_file:
        file_bytes = in_file.read()
    return file_bytes


def write_results_to_file(filename, results):
    with open("results/"+filename, 'w') as outfile:
        json.dump(results, outfile)


def run_simulation(vad, processing_type):

    file = "alice.mp3"
    benchmark_name = processing_type+"_vad" + str(vad)
    logging.info("STARTING BENCHMARK: " + benchmark_name)
    file_bytes = get_file_bytes(file)
    # p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    # p.daemon = True
    # p.start()
    t = threading.Thread(target=metrics_logger.logger, args=(benchmark_name + ".log",))
    t.start()
    if processing_type == "multiprocessor":
        service = MultiProcessorService()
    else:
        service = SingleThreadedService()

    result = service.process_audio(file_bytes, "mp3", vad)
    t.do_run = False
    t.join()
    write_results_to_file(benchmark_name + "_result.json", result)
    logging.info("ENDING BENCHMARK: " + benchmark_name)
    del file_bytes
    del service
    del result

if __name__ == "__main__":
    vads = [0,1,2,3]
    processing_types = ['multiprocessor','singlethreaded']

    if not os.path.exists("results"):
        os.makedirs("results")

    for vad in vads:
        for processing_type in processing_types:
            run_simulation(vad, processing_type)



    # p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    # p.daemon = True
    # p.start()


