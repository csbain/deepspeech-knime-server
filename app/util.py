import logging
import multiprocessing
import time
import subprocess, os, signal, sys
import signal, psutil
import sys

def format_time_duration(start, end):
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


def configure_logging(log_name):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def restart_flask_server():
    sys.exit("Forced exit via web app")


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def is_request_underway():
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    return True if len(children) > 0 else False
