import requests
import json

import pandas as pd
import numpy as np
import random
import os
import re

import datetime
import time

from pykospacing import Spacing
from googletrans import Translator

'C:/Users/su/OneDrive - 청주대학교 (1)/datasets/before/2022/[2022_01_03]Google_Map_Review'

class GoogleMapReview_Crawler:
    
    def __init__(self, wait_time=20, save_file_path='C:/Users/su/OneDrive - 청주대학교 (1)/datasets/before/2022/[2022_01_03]Google_Map_Review', encoding = 'utf-8'):
        self.wait_time = wait_time # 한 번 크롤링 후 sleep 시간
        self.save_file_path = save_file_path # 저장 경로 및 데이터 읽을 경로.
        self.encoding = encoding # encoding 종류
        self.spacing = Spacing() # 띄어쓰기 처리
        self.new_data = None # 기존 글 보다 최신글을 저장하기 위한 자료구조
        self.today_date = str(datetime.date.today()) # log를 남기기 위한 오늘 날짜
        self.folder_path = os.path.join(self.save_file_path, self.today_date) # 파일을 다운로드 하기 위한 경로
        self.translator = Translator() # 구글 번역기

    # url에서 데이터 가져오는 함수. 전처리 포함
    def get_data(self, data, data_length, columns_length, start):
        save_data = np.empty((0, columns_length))
        # 데이터의 길이만큼 하나씩 데이터 가지고 오기
        for n in range(data_length):
            name = data[n][0][1] # 이름
            text = data[n][3] # 리뷰글
            # 읽어온 텍스트에서 (Google 번역 제공) 다음부터, (원문)전까지만 데이터 사용.
            if text is not None:
                if '(원문)' in text:
                    text = text[15:text.find('(원문)')-2]
                # 개행문자 처리
                text = ' '.join(text.split())
                # text에서 이모지 제외
                emoji = re.compile(u'[\U00010000-\U0010FFFF]+', flags=re.UNICODE)
                if emoji.search(text) != None:
                    # print(text)
                    text = emoji.sub('', text)
                    # print(text)
                # text가 한글이 아니라면 번역
                reg = re.compile('[^ㄱ-힣0-9.,!@#$%^&*?;~()\[\]\+·\"\'♡♥\-: ]+')
                if reg.search(text) != None:
                    # print(f'{start+n+2}번째 글 번역했어요')
                    # print('---번역 전---\n', text)
                    text = self.translator.translate(text, dest='ko').text
                    if reg.search(text) != None:
                        text = self.translator.translate(text, dest='en').text
                        if reg.search(text) != None:
                            text = self.translator.translate(text, dest='ko').text
                    # print('---번역 후---\n', text)
                text = re.sub(r'[\s]',"", text)
                text = self.spacing(text)

            counting_star = int(data[n][4]) # 별점
            guide = data[n][12][1][12][0] # 가이드 유무
            guide = True if '지역' in guide else False
            
            time_stamp = int(data[n][27]) # 타임스탬프
            date_time = datetime.datetime.fromtimestamp(time_stamp/1000) # 날짜
            # numpy array로 데이터 적재
            save_data = np.append(save_data, [[name, text, counting_star, guide, date_time]], axis=0)
        return save_data

    # csv 파일로 데이터 저장
    def save2csv(self, save_data, columns, park_name, start, data_length):
        file_path = os.path.join(self.folder_path, park_name+'_'+self.today_date+'.csv')
        if data_length != 0:
            # 폴더가 없을 시 폴더 생성
            if not os.path.exists(self.folder_path):
                os.mkdir(self.folder_path)
            # 데이터 파일 저장
            df = pd.DataFrame(data=save_data, columns=columns)
            if not os.path.exists(file_path):
                df.to_csv(file_path, index=False, mode='w', encoding=self.encoding)
            else:
                df.to_csv(file_path, index=False, mode='a', encoding=self.encoding, header=False)

            # 진행상황 표시
            print(f'{start+1} ~ {start+data_length} data store, save file at {file_path}, data shape : {save_data.shape}')

            # 봇 감지 안당해보려고 wait 해봄.
            wait_time = random.randint(self.wait_time, self.wait_time+5)
            # wait_time = self.wait_time
            print(f'{wait_time}초 동안 기다리는중...')
            time.sleep(wait_time)

    # 데이터 맨앞에다가 삽입(최신순)할 수가 없으니까, 원본 데이터의 자료구조에 삽입 후 새로 write
    def save2csv_prepend(self, columns, park_name, start, origin_data):
        
        if self.new_data.shape[0] != 0:
            df_to_insert = pd.DataFrame(data=self.new_data, columns=columns)
            idx = 0 # 맨 위에 삽입
            temp1 = origin_data[origin_data.index < idx]
            temp2 = origin_data[origin_data.index >= idx]
            df = temp1.append(df_to_insert, ignore_index=True).append(temp2)

            file_path = os.path.join(self.folder_path, park_name+'_'+self.today_date+'.csv')
            
            df.to_csv(file_path, index=False, mode='w', encoding=self.encoding)

            # 진행상황 표시
            print(f'{start} ~ {start+len(self.new_data)-1} data store, save file at {file_path}, data shape : {self.new_data.shape}')
        else:
            print('there is no new data')

    # 데이터 파일 있는지 체크
    def check_data_file(self, park_name):
        file_path = os.path.join(self.folder_path, park_name+'_'+self.today_date+'.csv')
        if os.path.exists(file_path):
            read_dataset = pd.read_csv(file_path, encoding=self.encoding, parse_dates=['datetime'])
            # read_dataset = pd.read_csv(self.save_file_path + '/' + park_name + '.csv', encoding=self.encoding, parse_dates=['date'])
            try:
                first_data = read_dataset.head(1)['datetime'].item()
                read_dataset_length = len(read_dataset)
            except:
                first_data = None
                read_dataset_length = 0
            print(f'first_data : {first_data}, read_dataset_length : {read_dataset_length}')
        else:
            first_data = None
            read_dataset_length = 0
            read_dataset = None

        return first_data, read_dataset_length, read_dataset

    # url 값 변경
    def change_url_value(self, url, start, limit):
        # url에서 5번째와 6번째 느낌표의 위치 확인 후 url의 시작 값과 긁어올 개수 변경
        temp = 0
        arr_temp = list()
        for _ in range(7):
            temp = url.find('!', temp) + 1
            arr_temp.append(temp)
        url = url[ : arr_temp[-3] + 2] + str(start) + url[arr_temp[-2] - 1 : arr_temp[-2]+2] + str(limit) + url[arr_temp[-1]-1:]

        return url

    def run(self, park_names_urls, columns=['name', 'text', 'counting_star', 'guide', 'datetime']):
        # columns = ['name', 'text', 'counting_star', 'guide', 'datetime']
        columns_length = len(columns)
        
        # limit = 199 # 최대로 불러오는 데이터의 개수. 199개가 최댓값
        for park_name, url in park_names_urls.items():
            start = 0 # 데이터 불러오는 시작 번호
            self.new_data = np.empty((0, columns_length)) # 기존 글 보다 최신글을 저장하기 위한 자료구조. 초기화.
            # 데이터 유무 체크
            first_data, read_dataset_length, read_dataset = self.check_data_file(park_name)
            # url에서 데이터 가지고 오기
            while True:
                # limit = random.randint(150, 199)
                limit = 199
                url = self.change_url_value(url, start, limit)
                # url 요청 후 데이터가 있으면 수행, 없으면 while문 끝냄
                try:
                    resp = requests.get(url)
                    # 이름, 리뷰글, 별점 등의 데이터가 들어있는 변수
                    data = json.loads(resp.text[5:])[2]
                    # 데이터의 총 길이 변수
                    data_length = len(data)
                except:
                    print('there is no data')
                    break

                # 데이터의 길이만큼 이름, 리뷰글, 별점, 지역가이드 유무, 날짜 저장
                # 파일이 있다면 체크 후 데이터 저장
                if first_data is not None:
                    # 일단 데이터 로드
                    save_data = self.get_data(data, data_length, columns_length, start)
                    data_check = np.where(save_data[:, 4] == first_data)[0]
                    # csv 데이터에 url에서 불러온 데이터가 있다면
                    try:
                        data_check = data_check[0]
                    # 없다면
                    except:
                        data_check = None

                    # 첫번째 데이터가 나왔다면 data_check한 번호 까지만 저장한 후 start 값 변경
                    if data_check is not None:
                        self.new_data = np.append(self.new_data, save_data[:data_check], axis=0)

                        self.save2csv_prepend(columns, park_name, start, read_dataset)

                        start += read_dataset_length + 1
                        first_data = None
                        continue
                    # 파일은 있는데 아직 첫번째 데이터가 나오지 않았다면 데이터 임시 저장
                    # 
                    else:
                        self.new_data = np.append(self.new_data, save_data, axis=0)
                # 없다면 그냥 데이터 저장
                else:
                    save_data = self.get_data(data, data_length, columns_length, start)
                    self.save2csv(save_data, columns, park_name, start, data_length)

                # url 시작 번호와 긁어올 개수 변경
                start += limit
        print('************done!************')
        
if __name__ == '__main__':
    # 데이터 수집 후 저장

    # 여의도 공원
    yeouido = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3854130351592427969!2y1183578152943201358!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1sHRK-YczUNovVmAXu4Y2oBg!7e81'
    # 중마루 공원
    jungmaru = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3854130076605085461!2y4267646139674355142!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1sOMa_Ya6yErCb4-EP4_iVmAM!7e81'
    # 영등포 문래공원
    yeongdeungpo = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3854130152952927545!2y17858430781635199831!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1sHRK-YczUNovVmAXu4Y2oBg!7e81'
    # 송도 센트럴파크
    songdo = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3853805479816194631!2y16093307205238936118!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1ssLDSYbD3A4Wm2roPjL2FgAU!7e81'
    # 제주 한림공원
    hallim = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3822536565648423411!2y17250413333016456819!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1ssLDSYbD3A4Wm2roPjL2FgAU!7e81'
    
    # 올림픽공원
    olympic = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3854137217401812099!2y6789200060716786287!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s63fhYbeNCImC-Ab0iLeoCA!7e81'
    # 북서울 꿈의 숲
    north_seoul_dream_forest = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3854161582165462385!2y2062050188270673990!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s6njhYZqzHfan2roP5qOU2AI!7e81'
    # 서울숲
    seoul_forest = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3854135139763549739!2y15968524466520016538!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s5nnhYdfjDdeO2roP4_WF6As!7e81'
    # 남산공원
    namsan = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3854134522034812315!2y6087123368962069807!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1sCXrhYfCxK-ne2roPrJCsoAg!7e81'
    # 하늘공원
    haneul = 'https://www.google.co.kr/maps/preview/review/listentitiesreviews?authuser=0&hl=ko&gl=kr&pb=!1m2!1y3853750127748669791!2y12208586948369296920!2m2!1i0!2i10!3e2!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1sP3rhYc6oLeTf2roP15etuAw!7e81'

    urls = {'yeouido' : yeouido, 'olympic' : olympic, 'north_seoul_dream_forest' : north_seoul_dream_forest, 'seoul_forest' : seoul_forest, 'namsan' : namsan, 'haneul' : haneul}
    dir_path = './datasets/before'
    crawling_start = GoogleMapReview_Crawler()
    crawling_start.run(park_names_urls = urls)