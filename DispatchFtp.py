#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import time,datetime
import ConfigParser

# 调度脚本
def start():
    copy_index = ""
    while True:
        # 获取当前时间sec
        current_time_sec = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')[-2:]
        index = int(current_time_sec)/10-1
        # 获取存储的文件
        store_file = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')[0:15]
       
        if index == -1:
            index = 5
        
        # 调用拷贝方法
        if copy_index != index and ( 4 <= int(current_time_sec[-1]) <= 9 ):
            # 执行清理
            clean_file()
            # 调用拷贝
            event_file = "/dev/shm/event.done." + str(index)
            copy_file(event_file,store_file)
            copy_index = index

        time.sleep(1)

def clean_file():
    # 获取配置中清理文件时间,单位是min
    f = ConfigParser.ConfigParser()
    f.read('/opt/smc/hardware/conf/ftp_config.ini')
    clean_time = f.get('Basic','CleanTime')
    # 删除/opt/data/temp_data/大于配置时间的文件 
    #os.system("find /opt/data/temp_data/ -type f -mmin +{0} -print | xargs rm -rf".format(clean_time))
    for root,dirs,files in os.walk("/opt/data/temp_data/"):
        files=files
    store_dir = "/opt/data/temp_data/"
    for temp_file in files:
        current_time = int(time.time())
        last_modify_time  = int(os.path.getmtime(store_dir + temp_file))
        if (current_time - last_modify_time) / 60 > clean_time:
            os.remove(store_dir + temp_file)



def copy_file(event_file,store_file):
    event_content= os.popen("sed '1d' {0} >> /opt/data/temp_data/{1}".format(event_file,store_file)).read().replace("\n","")
    

if __name__ == "__main__":
    # 进程不存在调用
    process_count=os.popen("ps -ef | grep python | grep -v grep | grep \"dispatch_ftp\" | wc -l").read()
    # 创建文件夹
    if not os.path.exists("/opt/data/temp_data/"):
        os.makedirs("/opt/data/temp_data/")
    if int(process_count.replace("\n","")) < 2:
        start()
        copy_file()
