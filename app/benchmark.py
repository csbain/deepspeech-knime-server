import threading
import metrics_logger
from asr_service import ASRService
import logging
import json
import os
import gc
import multiprocessing
import argparse
import util

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')


def get_file_bytes(filename):
    with open(filename, "rb") as in_file:
        file_bytes = in_file.read()
    return file_bytes


def write_results_to_file(filename, results):
    with open("results/"+filename, 'w') as outfile:
        json.dump(results, outfile)


def run_simulation(vad, processes):
    file = "alice.mp3"

    cpu_count = multiprocessing.cpu_count()
    if util.is_int(processes):
        print("assigning " + processes + " processes")
        processes = int(processes)
    elif processes.upper() == "MAX":
        processes = cpu_count
    else: exit("Invalid processes value")


    benchmark_name = "processes"+str(processes)+"_vad" + str(vad)
    logging.info("STARTING BENCHMARK: " + benchmark_name)
    file_bytes = get_file_bytes(file)

    t = threading.Thread(target=metrics_logger.logger, args=(benchmark_name + ".log",))
    t.start()
    service = ASRService()
    result = service.process_audio(file_bytes, "mp3", vad, processes)
    t.do_run = False
    t.join()
    write_results_to_file(benchmark_name + "_result.json", result)
    logging.info("ENDING BENCHMARK: " + benchmark_name)
    del file_bytes
    del service
    del result


vads = [0,1,2,3]
processes_ammount = ["MAX"] + [str(i) for i in range(1, multiprocessing.cpu_count()+1)]
parser = argparse.ArgumentParser(description='Run benchmarks on Deepseech integration')
parser.add_argument('-v', '--vad', choices=vads, type=int, required=True)
parser.add_argument('-p', '--processes', choices=processes_ammount, required=True)
args = parser.parse_args()


if __name__ == "__main__":
    if not os.path.exists("results"):
        os.makedirs("results")
    run_simulation(args.vad, args.processes)


