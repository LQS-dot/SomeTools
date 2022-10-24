#!/usr/bin/python
# -*- coding:utf-8 -*-
from dispatch_ftp import *
from ftplib import FTP
from subprocess import Popen,PIPE,STDOUT
import ConfigParser,os,sys
import signal

# 超时退出类
class TimeOut(object):
    def time_out(self):
        raise TimeoutError

# 上传
def uploaded():
    f = ConfigParser.ConfigParser()
    f.read('/opt/smc/hardware/conf/ftp_config.ini')
    # ftp服务器ip
    Ip = f.get('Basic','Ip')
    # ftp服务器port
    Port = f.get('Basic','Port')
    # ftp的用户名
    username = f.get('Basic','User')
    # 密码
    password = f.get('Basic','Passwd')
    # bufsize = 1024
    login_info = "{0}:{1}@{2}".format(username,password,Ip)
    # 超时
    obj = TimeOut()
    signal.signal(signal.SIGALRM, obj.time_out)
    signal.alarm(600)
    
    store_dir = "/opt/data/temp_data/"
    for root,dirs,files in os.walk("/opt/data/temp_data/"):
        files=files
    for temp_file in files:
        current_time = int(time.time())
        last_modify_time  = int(os.path.getmtime(store_dir + temp_file))
        # 最后修改时间大于10分钟参与上传
        if (current_time - last_modify_time) / 60 > 85:
            p = Popen(['lftp', login_info], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            upload_file = store_dir + temp_file
            try:
                output = p.communicate(input='put {0}'.format(upload_file))
                if not output[0].replace("\n",""):
                    os.remove(upload_file)
                else:
                    clean_log()
                    with open("/opt/data/upload_result.txt","a+") as f:
                        f.write(output[0].replace("\n","")+"\n")
            except Exception:
                clean_log()
                with open("/opt/data/upload_result.txt","a+") as f:
                    f.write("put: Connect failed."+"\n")
                sys.exit()

if __name__ == "__main__":
    clean_file()
    uploaded()

