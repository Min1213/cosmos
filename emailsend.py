#Step 1. 필요한 모듈과 라이브러리를 로딩합니다.
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import sys
import re
import math
import numpy
import pandas as pd
import xlwt
 
import random
import os
 
import smtplib
from smtplib import SMTP
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
 
 
#Step 2. 사용자에게 검색어 키워드를 입력 받습니다.
print("=" *80)
print("매일경제 MBN")
print("=" *80)
 
query_txt = "코로나"
#query_txt = input('키워드를 입력해 주세요?:')
f_dir = 'c:\\data\\'
 
#저장할 파일위치와 이름을 지정합니다.
now = time.localtime() ##연,월,일,시,분,초의 정보
s = '%04d-%02d-%02d-%02d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
s_dir = s + "-" + "매일경제"
 
os.makedirs(f_dir + s_dir)    
os.chdir(f_dir + s_dir)   ##파일을 만들기 위해 폴더 이동하기
 
ff_name = f_dir + s_dir + '\\' + s + '-' + '매일경제-' + query_txt + '.txt'
fc_name = f_dir + s_dir + '\\' + s + '-' + '매일경제-' + query_txt + '.csv'
fx_name = f_dir + s_dir + '\\' + s + '-' + '매일경제-' + query_txt + '.xls'
 
#Step 3. 크롬 드라이버를 사용해서 웹 브라우저를 실행합니다.
s_time = time.time()
 
path = 'C:\Temp\chromedriver_90\chromedriver.exe'
driver = webdriver.Chrome(path)
 
driver.get('https://www.mk.co.kr/')
time.sleep(5)
 
#Step 4. 키워드 검색을 합니다.
#첫화면에서 오늘의 매경을 누른다.
driver.find_element_by_xpath('//*[@id="gnbbx"]/ul[2]/li[2]/a').click()
time.sleep(2) 
 
#키워드 검색을 한다.
element = driver.find_element_by_id('search_today_text') #매경 사이트 개발자
element.send_keys(query_txt)
 
driver.find_element_by_link_text('검색').click()
time.sleep(2)
 
#최근의 1일을 누른다.
driver.find_element_by_xpath('//*[@id="container_search"]/div[1]/div[3]/ul/li[2]/a').click()
time.sleep(2)
 
titles = []
bodys = []
 
##Step 5. 상세 기사를 검색해서 저장합니다.
for i in range(2,5):
    ##첫번째 게시글
    driver.find_element_by_xpath("""//*[@id="container_result"]/div[%s]/dl/dt[1]/a"""%i).click()
    time.sleep(2)
 
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
 
    article_title = soup.find('div', 'article_head').find('h3', 'article_title')
    article_title_text = article_title.get_text(strip=True)
    
    print(article_title_text)
    titles.append(article_title_text)
 
    article_body = soup.select_one('div.article_body')
    article_body_text = article_body.get_text().strip()
    
    print(article_body_text)
    bodys.append(article_body_text)
 
    ##페이지 뒤로 돌아가기
    driver.back()
    time.sleep(2)
 
 
mkData = pd.DataFrame()
mkData['제목']=titles
mkData['내용']=bodys
 
#txt 형식의 파일로 저장하기
f = open(ff_name, 'a', encoding='cp949')
f.write(str(bodys))
f.close()
 
#csv 형태로 저장하기
mkData.to_csv(fc_name, encoding="cp949")
 
#엑셀 형태로 저장하기
mkData.to_excel(fx_name)
 
e_time = time.time()    #검색이 종료된 시점의 timestamp
t_time = e_time - s_time
 
print("\n")
print("="*80)
print("총 소요시간은 %s 초 입니다." %round(t_time,1))
print("파일 저장 완료: txt 파일명: %s" %ff_name)
print("파일 저장 완료: csv 파일명: %s" %fc_name)
print("파일 저장 완료: xls 파일명: %s" %fx_name)
print("="*80)
 
driver.close()
 
#발송 이메일
fromaddress = '보내는사람 메일주소'
pw = '비밀번호'
 
#수신 이메일
toaddress = ['수신 메일주소1', '수신 메일주소2']
 
#이메일 제목
msg = MIMEMultipart()
subject = s + '-' + '매일경제-' + query_txt
msg['Subject'] = subject
 
#이메일 내용 입력
text = MIMEText('첨부파일 참조 부탁드립니다.')
 
#이메일 제목과 내용 합치기
msg.attach(text)

smtp_obj = smtplib.SMTP('smtp.gmail.com', 587) #587: google smtp 서버의 포트번호
smtp_obj.ehlo()
smtp_obj.starttls() #tls 방식으로 smtp 서버 접속
smtp_obj.login(fromaddress, pw) #fromaddres에 로그인
 
#파일 첨부
files = f_dir + s_dir
filenames = [os.path.join(files, f) for f in os.listdir(files)]
 
for file in filenames:
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(open(file, 'rb').read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="%s"' % file)
      msg.attach(part)
 
for i in toaddress:
    msg['To'] = i
    smtp_obj.sendmail(fromaddress, i, msg.as_string())
 
smtp_obj.quit()
 
print("정상종료")