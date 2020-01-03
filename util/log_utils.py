#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging.config
import os


log_dir = os.path.join("/Application/rep", "logs")
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

logging.config.fileConfig("/Application/rep/conf/logging.conf")
logger = logging.getLogger("root")
logger_receiver = logging.getLogger("receiver")
logger_refresh_result=logging.getLogger("refresh_result")


def getLogger():
    return logger


def get_receiver_Logger():
    return logger_receiver



def get_logger_refresh_result():
    return logger_refresh_result

