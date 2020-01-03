# encoding= utf-8
import logging.handlers
import datetime
import time
import pymongo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

#import importlib #py3
#importlib.reload(sys)#py3

reload(sys)#py2
sys.setdefaultencoding('utf8')

logger = logging.getLogger('cert_purge.log')

f_handler = logging.FileHandler('cert_purge.log')
f_handler.setLevel(logging.ERROR)
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s",datefmt=DATE_FORMAT))

logger.addHandler(f_handler)


HOST = '223.202.203.88'
DB_NAME_S1 = 'bermuda_s1'
port = 27017
usr = 'bermuda'
pwd = 'bermuda_refresh'
#db_name = 'bermuda'

def get_host(host,db_name):
    client = pymongo.MongoClient(host=host, port=port)
    db = client[db_name]
    db.authenticate(usr, pwd)
    return db
def make_validity_to_China(cert_time_dict):
    '''
    证书时间时区转换
    '''
    logger.debug('-----make_validity_to_China  cert_time_dict %s'%(cert_time_dict))
    res = {}
    for k, v in cert_time_dict.items():
        if 'Z' in v:
            logger.debug('-----make_validity_to_China  had Z ! ')
            #UTC
            _t = v[:-1]
            _date_obj = datetime.datetime.strptime(_t, '%Y%m%d%H%M%S')
            china_date = _date_obj + datetime.timedelta(hours=8)
            res[k] = china_date.strftime('%Y%m%d%H%M%S')
        elif '+' in v:
            logger.debug('-----make_validity_to_China  had + ! ')
            #带时区
            _date_s = v[:-5]
            if v[-4:] == '0800':
                res[k] = _date_s
            else:
                _h = int(v[-4:-2])
                _m = int(v[-2:])
                _date_obj = datetime.datetime.strptime(_date_s, '%Y%m%d%H%M%S')
                china_date = _date_obj - datetime.timedelta(hours=_h, minutes=_m) + datetime.timedelta(hours=8)
                res[k] = china_date.strftime('%Y%m%d%H%M%S')
        elif '-' in v:
            logger.debug('-----make_validity_to_China  had - ! ')
            #带时区
            _h = int(v[-4:-2])
            _m = int(v[-2:])
            _date_obj = datetime.datetime.strptime(_date_s, '%Y%m%d%H%M%S')
            china_date = _date_obj + datetime.timedelta(hours=_h, minutes=_m) + datetime.timedelta(hours=8)
            res[k] = china_date.strftime('%Y%m%d%H%M%S')
        else:
            res[k] = v
    return res

def write_statistical(cert_purge_list):
    header_list = ["用户名","证书别名","存储文件名","开始时间","过期时间"]

    theader = '<th>{0}</th>'.format('</th><th>'.join(header_list))
    trs = []
    for cert_purge in cert_purge_list:
        ts = [cert_purge.get('username'),cert_purge.get('cert_alias'),cert_purge.get('save_name'),cert_purge.get('begin_time'),cert_purge.get('end_time')]
        print ts
        trs.append('<td>{0}</td>'.format('</td><td>'.join(ts)))
    table = '<table border="1">\n<thead><tr>{0}</tr></thead>\n<tbody>\n<tr>{1}</tr></tbody></table>'\
        .format(theader,'</tr>\n<tr>'.join(trs))
    print table
    return table

# 发邮件
def send_email(to_addrs, subject, content):
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
    except Exception, ex:
        pass
    s.sendmail(from_addrs, to_addrs, msg.as_string())
    s.quit()

def get_cert_purge_list():
    monitor_db = get_host(HOST,DB_NAME_S1)
    all_cert = monitor_db.cert_detail.find({'t_id':{'$exists': False}})
    #nowtime = int(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    nowtime = int((datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y%m%d%H%M%S'))
    cert_list = []
    cert_purge_list = []
    num = 0
    for cert in all_cert:
        cert['validity_china'] = make_validity_to_China(cert['validity'])
        t = int(cert['validity_china']['end_time'])
        tt = t - nowtime
        if tt < 0:
            num += 1
            last_dict = {}
            last_dict['username'] = cert.get("username")
            last_dict['cert_alias'] = cert.get("cert_alias")
            last_dict['save_name'] = cert.get("save_name")
            last_dict['begin_time'] = datetime.datetime.strptime(cert["validity_china"]["begin_time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")#cert["validity_china"]["begin_time"]
            last_dict['end_time'] = datetime.datetime.strptime(cert["validity_china"]["end_time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")#cert["validity_china"]["end_time"]
            #cert_list.append(cert.get("cert_alias"))
            cert_purge_list.append(last_dict)
    last_list = sorted(cert_purge_list,key=lambda cer:cer.get('username'))
    #print cert_purge_list
    #print num
    return last_list
    # totalpage = int(sum / (per_page * 1.00))
    # curpage = query_args.get("curpage")
    # certs_dict = {"certs": cert_list[(curpage - 1) * per_page:curpage * per_page - 1], "totalpage": totalpage}
    # for c in certs_dict["certs"]:
    #     c["validity_china"]["end_time"] = datetime.strptime(c["validity_china"]["end_time"], "%Y%m%d%H%M%S")
    #     c["validity_china"]["begin_time"] = datetime.strptime(c["validity_china"]["begin_time"], "%Y%m%d%H%M%S")
    #     c['c_type'] = 'expired'
def main():
    purge_list = get_cert_purge_list()
    content = write_statistical(purge_list)
    to_addrs = ['pengfei.hao@chinacache.com']
    subject = '过期证书以及即将过期证书'
    send_email(to_addrs, subject, content)
if __name__ == "__main__":
    main()
    pass
