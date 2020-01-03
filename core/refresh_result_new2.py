#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2017-11-13

"""
from __future__ import with_statement
import simplejson as json
import sys
# log
import traceback, logging, time
from datetime import datetime
from core import my_queue as queue
from core import database
# from util import log_utils
from core.config import config
# from util.tools import delete_urlid_host, get_mongo_str
from util.tools import get_mongo_str

# logger = logging.getLogger('router')
# logger.setLevel(logging.DEBUG)

# logger = log_utils.get_logger_refresh_result()


# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
logfile = '/Application/rep/logs/router.log'
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

db_s1 = database.s1_db_session()


class Refresh_router(object):
    def __init__(self, batch_size=10000, package_size=60):

        self.batch_size = batch_size
        self.package_size = package_size
        self.merged_refresh = {}
        # self.merged_refresh_dir={}

    def run(self):
        logger.debug("refresh_router.start")
        self.refresh_router()
        logger.debug("refresh_router.end")

    def refresh_router(self, queue_name='result_task'):
        '''
        回调数据打包
        '''
        # try:
        # messages = queue.get(queue_name, self.batch_size)
        # print(queue_name)
        # print(self.batch_size)
        # messages = queue.get(queue_name, self.batch_size)
        # messages = queue.get("result_task", 10000)
        try:
            messages = queue.get("result_task", 10000)
        except Exception as e:
            logger.warning('get result queue error {}'.format(traceback.format_exc(e)))
            messages = []
        # print (message)
        if not messages:
            return
        try:
            for body in messages:
                # logger.debug('---------'+ body +'-------------------')
                # print(body)
                # task = json.loads(body)
                try:
                    task = json.loads(body)
                except Exception as e:
                    logger.warning('json loads error {}'.format(traceback.format_exc(e)))
                    # if isinstance(task, str):
                    # task = json.loads(task)
                # logger.debug(task)
                # logger.debug('router for refresh: %s' % task.get('session_id'))
                # self.merge_refresh(task)
                try:
                    self.merge_refresh_new(task)
                except Exception as e:
                    logger.warning('chong zu error:{}'.format(traceback.format_exc(e)))
        except Exception as e:
            logger.warning('for xunhuan error {},{}'.format(traceback.format_exc(e), messages))
        # for key in self.merged_refresh.iterkeys():
        try:
            for key in self.merged_refresh:
                try:
                    self.update_refresh_result(self.merged_refresh.pop(key))
                except Exception as e:
                    logger.warning('refresh update error:{}'.format(traceback.format_exc(e)))
        except Exception as e:
            logger.warning('error merged_refresh error:{}'.format(traceback.format_exc(e)))
            # except Exception as e:
            #    #logger.warning('refresh_router %s work error:%s' %(queue_name, traceback.format_exc(e)))
            #    logger.warning('refresh_router %s 111111work error:%s' %(queue_name, e))
            #    #print ('refresh_router %s work error:%s' %(queue_name, traceback.format_exc(e)))
            #    print('--------------error-----------------')

    # def merge_refresh(self, task):
    #     session_id = task['session_id']
    #     self.merged_refresh.setdefault(session_id, []).append(task)
    #     if len(self.merged_refresh.get(session_id)) > self.package_size:
    #         self.update_refresh_result(self.merged_refresh.pop(session_id))

    def merge_refresh_new(self, task):
        session_id = task['session_id']
        logger.debug("refresh_router :{}|{}|{}".format(session_id, task.get('host'), task.get('hostname')))
        db_key = get_mongo_str(session_id, 10)
        # if not db_key:
        #     logger.warn('dont get the key:%s' % (session_id))

        self.merged_refresh.setdefault(db_key, []).append(task)
        if len(self.merged_refresh.get(db_key)) > self.package_size:
            self.update_refresh_result(self.merged_refresh.pop(db_key))

    def update_refresh_result(self, results):
        logger.debug('update_refresh_result is {}'.format(results))
        if not results:
            return
        logger.debug('update_refresh_result number:%s' % (len(results)))
        for result in results:
            timestr = result['time']
            result['time'] = datetime.strptime(timestr,
                                               '%Y-%m-%d %H:%M:%S %f')  # time.mktime(time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        #     # url_id = result.get('session_id')
        #     # host = result.get('host')
        #     # result_code = result.get('result')
        #     # try:
        #     #     #if result.has_key('result_gzip'):
        #     #     if 'result_gzip' in result:
        #     #
        #     #         result_gzip_code = result.get('result_gzip', '0')
        #     #         if str(result_code) == '200' and str(result_gzip_code) == '200':
        #     #             delete_urlid_host(url_id, host)
        #     #     else:
        #     #         if str(result_code) == '200':
        #     #             delete_urlid_host(url_id, host)
        #     # except Exception as e:
        #     #     #logger.debug('refresh result error :%s' % traceback.format_exc(e))
        #     #     logger.debug('refresh result error :%s' % (e))
        str_num = ''
        try:
            num_str = config.get('refresh_result', 'num')
            str_num = get_mongo_str(str(results[0].get('session_id')), num_str)
        except Exception as e:
            logger.debug('get number of refresh_result error:%s' % (e))

        try:

            # db_s1['refresh_result' + str_num].insert_many(results,ordered=False)
            logger.debug('insert mongodb  is {}'.format(results))
            db_s1['refresh_result' + str_num].insert_many(results, ordered=False)
            logger.debug('insert mongodb end')

            time.sleep(0.05)

            #logger.debug('update_refresh_result success, session_id:%s' % (result.get('session_id')))
        except Exception as  e:
            #logger.warn('update_refresh_result error:%s, session_id:%s' % (traceback.format_exc(e), result.get('session_id')))
            # logger.info('update_refresh_result error:%s, session_id:%s' % (e,result.get('session_id')))
            logger.warning('insert mongodb is error{}{}'.format(traceback.format_exc(e),results))

    def load_task(self, task):
        '''
            解析接口的task

        Parameters
        ----------
        task : 刷新任务，JSON 格式

        Returns
        -------
        {"urls":["http://***1.jbp","http://***2.jbp"],
　　      "dirs":["http://***/","http://d***2/"],
　　      "callback":{"url":"http://***",
　　                  "email":["mail1","mail2"],
                    "acptNotice":true}}
        '''
        try:
            return json.loads(task)
        except Exception:
            logger.warn(task, exc_info=sys.exc_info())


if __name__ == "__main__":
    logger.debug("router begining...")
    now = datetime.now()
    print (now)
    router = Refresh_router()
    router.run()
    end = datetime.now()
    print (end - now)
    logger.debug("router end.")
    # message = queue.get("result_task", 1000)
    # print(message)
