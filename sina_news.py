# -*- coding:utf-8 -*-

 
from lxml.html import etree
import  os
import pymysql
import logging
import random  
from selenium import webdriver
 
import json
import time 
from time import sleep
 
from  Config  import *
# 通过下面的方式进行简单配置输出方式与日志级别
import logging
import  datetime
global rows
global values
url='http://finance.sina.com.cn/7x24/?tag=10'
basedir=os.path.dirname(os.path.realpath(__file__))
logfile="%s\\log\\sina_%s.log" %(basedir,datetime.datetime.now().strftime("%Y-%m-%d"))   
logging.basicConfig(filename=logfile, level=logging.DEBUG,format='%(asctime)s  %(message)s')

logfilename="%s\\DATA\\sina_%s.sql" %(basedir,datetime.datetime.now().strftime("%Y-%m-%d"))  
 
start = time.time()
infor="Import all  stocks begins!"
logging.info(infor)	 
rows=0
values=[] 
header="INSERT INTO `sina_news` (`n_date`, `n_time`, `content`) VALUES" 
middle="(%s, %s, %s)"

query =header+middle


def write_content_to_file(filename,message, encoding='utf-8'):
    file_object = open(filename,'a+')
    try:
        #file_object.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'\t'+message+'\n')
        file_object.write(message+'\n')
    finally:
        file_object.close()
    
def writeFile(message):
    file_object = open(logfilename,'w+', encoding='utf-8')
    try:
        #file_object.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'\t'+message+'\n')
        file_object.write(message+'\n')
    finally:
        file_object.close()
        
 
        
    
def  insert_query(query,values):
 
    if  len(values) > 0 :
        sqlstr=json.JSONEncoder().encode(values)
        sqlstr=sqlstr.replace('[', '(').replace(']',')').replace('((', '(').replace('))',')')
        sqlstr= header+sqlstr
        writeFile(sqlstr) 
        connection = pymysql.connect(host=HOST,port=int(PORT),user=USERNAME,passwd=PASSWORD,db=DATABASE,charset='utf8')
        mycursor= connection.cursor()
        
        try:
            # Execute the SQL command
           
            mycursor.executemany(query, values)
            connection.commit()
            affected_rows = mycursor.rowcount
            if affected_rows:
                print("Number of rows affected : {}".format(affected_rows))
                logging.info("Number of rows affected : {}".format(affected_rows))
            else:
                print('0 row  affected!')
                logging.info('0 row  affected!') 
            values=[]
            sqlstr=""
        except  Exception as e:
            #writeFile("Exeception occured:{}".format(e))
            print("Exeception occured:{}".format(e))
            logging.error("Exeception occured:{}".format(e))
            connection.rollback()
        finally:
            mycursor.close()
            connection.close()
 
 
def scroll_top(driver):
    if driver.name == "chrome":
        js = "var q=document.body.scrollTop=0"
    else:
        js = "var q=document.documentElement.scrollTop=0"
    return driver.execute_script(js)
         
 
def scroll_foot(driver):
    if driver.name == "chrome":
        js = "var q=window.scrollTo(0, document.body.scrollHeight);"
    else:
        js = "var q=document.documentElement.scrollTop=100000"
    return driver.execute_script(js)
         
def write_text(filename, info):
    """  
    :param info:  
    :return: none
    """
    #  
    with open(filename, 'a+') as fp:  
        fp.write(str(info))
        fp.write('\n')
        fp.write('\n') 
     
def sroll_multi(driver):
    loopCounter = 0
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    while True:
        if loopCounter >5500:
            break; # if the account follows a ton of people, its probably a bot, cut it off
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randint(2,9))
        newHeight = driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
            break
        lastHeight = newHeight
        loopCounter = loopCounter + 1
 
            
options = webdriver.ChromeOptions()  
   
options.add_argument("--headless")  
driver = webdriver.Chrome(chrome_options = options,executable_path='D:\\chromedriver.exe')
driver.implicitly_wait(30)
driver.maximize_window()
   
driver.implicitly_wait(10)
# driver.maximize_window()
driver.get(url)
sroll_multi(driver)  
  
data_secs = driver.find_elements_by_xpath('//*[@id="liveList01"]/div')
for data_sec  in  data_secs:
    day = data_sec.get_attribute('data-time')
    hour_min= data_sec.find_element_by_class_name('bd_i_time_c')
    content= data_sec.find_element_by_class_name('bd_i_txt_c')
    print(day,content.text)
     
    filename="%s\\data\\sina24x_%s.txt" %(basedir,day)
    
    value=[  day , hour_min.text, content.text]
    filecontent= hour_min.text+'\t'+ content.text
    write_content_to_file(filename, filecontent)
    values.append(value)
  
    rows=rows+1
    if (rows % 50 == 0):
        insert_query(query,values)
        values=[]
if len(values) > 0 :            
    insert_query(query,values)
    values=[]
