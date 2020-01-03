#-*- coding:utf-8 -*-
import time
import datetime
import pymongo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson.objectid import ObjectId
import copy


db_host = '223.202.203.93'
db1_host = '223.202.203.88'
#to_addrs_eamil = ['pengfei.hao@chinacache.com','huan.ma@chinacache.com']
to_addrs_eamil = ['pengfei.hao@chinacache.com','huan.ma@chinacache.com','shanshan.lu@chinacache.com','chunjing.li@chinacache.com']
#to_addrs_eamil = ['pengfei.hao@chinacache.com']

to_addrs_eamil_error = ['pengfei.hao@chinacache.com','huan.ma@chinacache.com','shanshan.lu@chinacache.com','chunjing.li@chinacache.com']
#to_addrs_eamil_error = ['pengfei.hao@chinacache.com']#,'huan.ma@chinacache.com','shanshan.lu@chinacache.com','chunjing.li@chinacache.com']

def get_host(host,db_name):
    client = pymongo.MongoClient(host=host, port=27017)
    db = client[db_name]
    db.authenticate('bermuda', 'bermuda_refresh')
    return db
def get_url(username,act_time,end_time):
    db_s = get_host(db_host,'bermuda')
    print (act_time)
    print (end_time)
    url_list = db_s['url'].find({'parent':username,"status" : {"$nin":["INVALID","PROGRESS"]},'created_time':{'$gt':act_time,'$lt':end_time}})
    #url_list = db_s['url'].find({'parent': username, "status": "FAILED",
    #                             'created_time': {'$gt': act_time, '$lt': end_time}})
    url_list = db_s['url'].find({"r_id" : ObjectId("5b4c51b4e2c9fb25832e6c56")})
    dev_dict = {}
    url_dict = {}
    url_detail = {}
    sessiond_list = []
    for url in url_list:
        print (url)
        sessiond_id = str(url['_id'])
        url_url = url.get('url')
        url_detail[sessiond_id] = url_url
        dev_id = url.get('dev_id')
        if dev_dict.get(str(dev_id)):
            dev_value = dev_dict.get(str(dev_id))
        else:
            dev_detail = db_s['device'].find_one({'_id':dev_id})
            devs_list = dev_detail.get("devices").values()
            dev_dict[str(dev_id)] = devs_list
            dev_value = devs_list
        url_dict[sessiond_id] = dev_value
        sessiond_list.append(sessiond_id)
    #print url_detail,sessiond_list,url_dict
    return url_detail,sessiond_list,url_dict

def get_rep(sessiond_list):
    db_s1 = get_host(db1_host, 'bermuda_s1')
    rep_url_dict = {}
    for sessiond_id in sessiond_list:
        mon_key = get_mongo_str(sessiond_id)
        rep_url_dict[sessiond_id] = db_s1['refresh_result{0}'.format(mon_key)].find({'session_id':sessiond_id})
    #print rep_url_dict
    return rep_url_dict
def get_result(url_detail,db_url_dict,rep_url_dict):
    result_dict = {}
    error_dict = {}

    for session_id in db_url_dict:
        if session_id not in rep_url_dict:
            continue
        key_url = url_detail.get(session_id)
        dev_list = db_url_dict[session_id]
        host_list = []
        host_name_dict ={}
        # name_host_dict ={}
        for dev in dev_list:
            host = dev.get('host')
            name = dev.get('name')
            status = dev.get('status')
            dev_type = dev.get('type')
            if status != 'SUSPEND' and dev_type =="HPCC":
                #print name
                host_name_dict[host] = name.encode("utf-8").lower()
                # name_host_dict[name] = host
                host_list.append(host)
        rep_dev_list = rep_url_dict.get(session_id)
        more_have = []
        more_have_dev =[]
        error_device = []
        for rep_dev in rep_dev_list:
            if rep_dev.get('result') == "200":
                # name = host_name_dict.get(rep_dev.get('host'))
                # if name:
                #     host_name_dict.pop(rep_dev.get('host'))
                #     name_host_dict.pop(name)
                #     error_device.append(name)
                # else:
                #     error_device.append(rep_dev.get('host'))
                rep_name = rep_dev.get('hostname').encode("utf-8").lower()
                rep_host = rep_dev.get('host')
                try:
                    host_list.remove(rep_host)
                except Exception as e:
                    more_have.append(rep_host)
                    more_have_dev.append(rep_name)
                    pass
            else:
                try:
                    error_device.append(rep_dev.get('hostname').encode("utf-8"))
                except Exception as e:
                    pass
        print ("dev mor ---------------{0}----".format(more_have_dev))
        if host_list:
            host_list_name_list = []
            for key_ip in host_list:
                host_list_name_list.append(host_name_dict.get(key_ip, None))
            print ("host dev --------{0}---------".format(host_list_name_list))
            if len(more_have)< len(host_list):
                error_dict[session_id] ={'url':key_url,'status':'false'}
            host_list_copy = copy.deepcopy(host_list_name_list)
            for host_name_key in host_list_name_list:
                try:
                    more_have_dev.remove(host_name_key)
                    host_list_copy.remove(host_name_key)
                    #host_list.remove(host_key)
                except Exception as e:
                    print ('------error-----')
                    pass
            if host_list_copy:
                #result_dict[session_id] ={'url':key_url,'status':'success' if len(more_have)>=len(host_list) else 'false','rep_num':len(more_have),'bermuda_num':len(host_list),'bermuda_host': host_list,'rep_more':more_have,'error_dev_list':host_list_name_list,'rep_dev_name':more_have_dev}
                result_dict[session_id] = {'url': key_url,
                                       'status':  'false',
                                       'rep_num': len(more_have), 'bermuda_num': len(host_list),
                                       'bermuda_host': host_list, 'rep_more': more_have,
                                       'error_dev_list': host_list_copy, 'rep_dev_name': more_have_dev,'!200':error_device}

    #print result_dict
    return result_dict,error_dict

def get_mongo_str(str_number):

    try:
        int_10 = int('0x' + str_number[:8], 16)
        return_t = int_10 % int(10)
        return str(return_t)
        # print int_10
    except Exception as e:
        return 'ddd'




# 发邮件
def send(to_addrs, subject, content):
    msg = MIMEMultipart()
    from_addrs = 'nocalert@chinacache.com'
    msg['Subject'] = subject
    msg['From'] = from_addrs
    msgText = MIMEText(content, 'html', 'utf-8')
    msg.attach(msgText)
    if type(to_addrs) == str:
        msg['To'] = to_addrs
    elif type(to_addrs) == list:
        msg['To'] = ','.join(to_addrs)
    s = smtplib.SMTP('anonymousrelay.chinacache.com')
    try:
        s.ehlo()
        s.starttls()
        s.ehlo()
    except Exception as ex:
        pass
    s.sendmail(from_addrs, to_addrs, msg.as_string())
    s.quit()

def run():
    now = datetime.datetime.now()
    a_now = now - datetime.timedelta(minutes=11)
    end = now - datetime.timedelta(minutes=5)

    userName_list = ['pingan']#可配置
    email_username_dict = {'pingan':to_addrs_eamil}#可配置
    error_email_username_dict = {'pingan':to_addrs_eamil_error}
    error_messages = {}
    messages = {}
    for username in userName_list:
        url_detail,sessiond_list, url_dict = get_url(username,a_now,end)
        rep_dict = get_rep(sessiond_list)
        message,error_mess = get_result(url_detail,url_dict,rep_dict)
        #messages.append(message)
        if message:
            messages[username] = message
        if error_mess:
            error_messages[username] = error_mess
    #print (messages)
    for user_name in messages:
        to_email_name =email_username_dict.get(user_name)
        content = messages.get(user_name)
        if content:
            content = str(content)
            print (content)
            send(to_email_name,'刷新回调真实结果',content)
    print("----------------------------------------")
    for error_user_name in error_messages:
        to_error_email_name =error_email_username_dict.get(error_user_name)
        content_error = error_messages.get(error_user_name)
        if content_error:
            content_error = str(content_error)
            print (content_error)
            send(to_error_email_name,'刷新回调失败',content_error)

if __name__ =="__main__":
    run()
