#coding=utf-8
import urllib2
import urllib
import requests
from lxml import etree
import time
import re
import os
import json
import xlsxwriter
import threading
import multiprocessing
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#返回全系列列表
def get_series():
    ar=[]
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    url='https://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=1'
    html=requests.get(url,header)
    js_data=html.json()
    html.close()
    series_factory='https://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=3&value='
    brand_list=js_data['result']['branditems']
    for list in brand_list:
        url=series_factory+str(list['id'])
        u=(list['name'],url)
        ar.append(u)
    return ar  #(众泰,https://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=3&value=94)

def get_last_url(name,url):
    #global lock
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    lock.acquire()
    try:
        resource=requests.get(url,header)
        data=resource.json()
        for car_id in data['result']['factoryitems']:
            for car_list in car_id['seriesitems']:
                get_price(name,car_list['name'],car_list['id'])
    except Exception,e:
        print e
    finally:
        lock.release()

def get_price(car_factory,car_name,car_id):
    global k
    rooturl='https://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=5&value={}'.format(car_id)
    res=requests.get(rooturl)
    data=res.json()
    res.close()
    spec_url='https://www.autohome.com.cn/spec/'
    for da in data['result']['yearitems']:
        for d in da['specitems']:
            xlsheet.write(k,0,car_factory)
            xlsheet.write(k,1,car_name)
            xlsheet.write(k,2,d['name'])
            xlsheet.write(k,3,d['minprice'])
            xlsheet.write(k,4,d['maxprice'])
            xlsheet.write(k,5,'{}{}/'.format(spec_url,d['id']))
            k+=1

if __name__=='__main__':
    test=get_series()
    k=0
    th=[]
    lock=threading.Lock()
    xlsbook=xlsxwriter.Workbook('autocar.xlsx')
    xlsheet=xlsbook.add_worksheet('sh')
    for t in test:
        t0=t[0]
        t1=t[1]
        threads=threading.Thread(target=get_last_url,args=(t0,t1,))
        th.append(threads)
    for thread in th:
        thread.start()
    for thread in th:
        thread.join()
    xlsbook.close()

