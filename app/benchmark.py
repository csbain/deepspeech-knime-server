import logging
import re
import threading
from multiprocessing import Process
import metrics_logger
from MultiProcessorService import MultiProcessorService
from SingleThreadedService import SingleThreadedService


def get_file_bytes(filename):
    bytes = None
    with open(file, "rb") as in_file:
        bytes = in_file.read()
    return bytes


def write_results_to_file(filename, results):
    with open(filename, "w") as log:
        log.write(results)


if __name__ == "__main__":
    sample_file = "alice.mp3"
    file = "alice.mp3"
    extensions = re.findall(r'\.([^.]+)', file)

    vad = 0
    benchmark = "multiprocessor_vad" + str(vad)
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = MultiProcessorService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)

    benchmark = "singlethreaded_vad0"
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = SingleThreadedService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)

    vad = 1
    benchmark = "multiprocessor_vad" + str(vad)
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = MultiProcessorService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)

    benchmark = "singlethreaded_vad0"
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = SingleThreadedService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)

    vad = 2
    benchmark = "multiprocessor_vad" + str(vad)
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = MultiProcessorService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)

    benchmark = "singlethreaded_vad0"
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = SingleThreadedService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)

    vad = 3
    benchmark = "multiprocessor_vad" + str(vad)
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = MultiProcessorService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)

    benchmark = "singlethreaded_vad0"
    logging.info("STARTING BENCHMARK: " + benchmark)
    p = Process(target=metrics_logger.logger, args=(benchmark + ".log",))
    p.start()
    bytes = get_file_bytes(file)
    service = SingleThreadedService()
    result = service.process_audio(bytes, extensions[0], vad)
    write_results_to_file(benchmark + "_result.json", result)
    del bytes
    del service
    del result
    p.join()
    logging.info("ENDING BENCHMARK: " + benchmark)
