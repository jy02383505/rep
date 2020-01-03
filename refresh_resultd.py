# -*- coding:utf-8 -*-
"""
Created on 2017-11-21

"""
import os
import logging
from core.refresh_result import Refresh_router
#from util import log_utils
import time
import threading


logger = logging

def run():
    logger.debug("refresh begining...")
    #while True:
    try:
        router = Refresh_router()
        router.run()
    except Exception as e:
        logger.debug(e.message)
    #time.sleep(5)
    logger.debug("refresh end.")
    #os._exit(0) # fix :there are threads, not exit properly
def main():
    while True:
        th=threading.Thread(target=run)
        th.start()
        time.sleep(20)


def main3():
    # while True:
    Ts = []
    for i in range(10):
        th = threading.Thread(target=run)
        Ts.append(th)
    for thr in Ts:
        thr.start()
    for th in Ts:
        threading.Thread.join(th)
# def main():
#     logger.debug("refresh begining...")
#     while True:
#         router = Refresh_router()
#         router.run()
#         time.sleep(5)
#     logger.debug("refresh end.")
#     os._exit(0) # fix :there are threads, not exit properly

if __name__ == "__main__":
    main()

