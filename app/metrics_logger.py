import datetime
import time
import os
import psutil
import threading
import shared_params
import logging

def logger(log_file=shared_params.DEFAULT_METRICS_LOG_FILE):
    delete_logfile_if_exists(log_file)
    headings = "datetime,free_mem,free_swap,free_tmp_part,free_cpu"
    write_to_logfile(log_file, headings)
    starttime = time.time()
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        datetimestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory = psutil.virtual_memory().percent
        swap = psutil.swap_memory().percent
        tmp_space = psutil.disk_usage('/tmp').percent
        cpu = psutil.cpu_percent(interval=None, percpu=True)
        processor_stats = ','.join(str(e) for e in cpu)
        log_line = datetimestr + "," + str(memory) + "," + str(swap) + "," + str(tmp_space) + "," + str(processor_stats)
        # logging.debug(log_line)
        # print(log_line)
        write_to_logfile(log_file, log_line)
        time.sleep(5.0 - ((time.time() - starttime) % 5.0))


def write_to_logfile(log_file, string):
    with open("results/"+log_file, "a+") as f:
        f.write(string+"\r\n")


def delete_logfile_if_exists(log_file):
    try:
        os.remove("results/"+log_file)
    except OSError:
        pass
