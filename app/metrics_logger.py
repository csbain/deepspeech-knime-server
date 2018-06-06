import datetime
import os
import psutil
import time

import SharedParams


def logger(log_file=SharedParams.DEFAULT_METRICS_LOG_FILE):
    delete_logfile_if_exists(log_file)
    headings = "datetime,free_mem,free_swap,free_tmp_part,free_cpu"
    write_to_logfile(log_file, headings)
    starttime = time.time()

    while True:
        datetimestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory = psutil.virtual_memory().percent
        swap = psutil.swap_memory().percent
        tmp_space = psutil.disk_usage('/tmp').percent
        cpu = psutil.cpu_percent(interval=None, percpu=True)
        processor_stats = ','.join(str(e) for e in cpu)
        log_line = datetimestr + "," + str(memory) + "," + str(swap) + "," + str(tmp_space) + "," + str(processor_stats)
        # print(log_line)
        write_to_logfile(log_file, log_line)
        time.sleep(30.0 - ((time.time() - starttime) % 30.0))


def write_to_logfile(log_file, string):
    with open(log_file, "a") as log:
        log.write(string)


def delete_logfile_if_exists(log_file):
    try:
        os.remove(log_file)
    except OSError:
        pass
