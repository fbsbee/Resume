import os
import datetime
import numpy as np
import pandas as pd
import timeit
import json

import threading
import asyncio
from concurrent.futures import ProcessPoolExecutor

from konlpy.tag import Kkma, Okt
from konlpy.utils import pprint

# 1.
# 각 파일들을 비동기로 실행
# 멀티 프로세싱으로 파일 내에서 데이터 처리

# or 
# 2.
# 각 파일들을 멀티 프로세싱으로 실행
# 비동기로 파일 내에서 데이터 처리
# 무엇이 더 빠른가?

# import matplotlib.pyplot as plt
# from wordcloud import WordCloud

# # 자신의 컴퓨터 환경에 맞는 한글 폰트 경로를 설정
# font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

# wc = WordCloud(width = 1000, height = 600, background_color="white", font_path=font_path)
# plt.imshow(wc.generate_from_frequencies(kolaw.vocab()))
# plt.axis("off")
# plt.show()

# 고유 ID에 +1

# 단어에 고유 ID를 부여해주는 클래스
class VocabDict:
    def __init__(self):
        self.d = {}  # 단어->단어ID로 변환할때 사용
        self.w = []  # 단어ID->단어로 변환할 때 사용
 
    def getIdOrAdd(self, word):
        # 단어가 이미 사전에 등록된 것이면 해당하는 ID를 돌려주고
        if word in self.d:
            return self.d[word]
        # 그렇지 않으면 새로 사전에 등록하고 ID를 부여함
        self.d[word] = len(self.d)
        self.w.append(word)
        return len(self.d) - 1
 
    # 단어가 사전에 등록되어있는 경우 ID를 돌려주고
    def getId(self, word):
        if word in self.d:
            return self.d[word]
        # 그렇지 않은 경우 -1을 돌려줌
        return -1
    # id를 통해 단어 획득
    def getWord(self, id):
        return self.w[id]

class NLP:
    
    def __init__(self, read_dir_path='./datasets/before', save_dir_path=None, encoding = 'utf-8'):
        self.read_dir_path = read_dir_path # 저장된 파일 경로
        
        self.save_dir_path = save_dir_path # 저장할 파일 경로

        self.encoding = encoding # encoding 방법
        self.vDict = VocabDict()
        self.vDictFiltered = VocabDict()
        self.wcount = {}  # 단어별 빈도가 저장될 dict

        self.kkma = Kkma() # 자연어 처리 할 모듈 불러오기
        self.okt = Okt()

        self.cpu_count = os.cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.cpu_count)

    # 저장된 파일 경로에서 저장할 파일 경로로 변경
    def change_dir(self, read_dir_path, save_dir_path=None):
        word = 'before'
        temp = read_dir_path.find(word)
        if temp == -1 and save_dir_path is not None:
            save_dir_path = save_dir_path
        else:
            save_dir_path = read_dir_path[:temp] + 'after' + read_dir_path[temp+len(word):]
        return save_dir_path
    
    # 파일 경로 반환 함수
    def read_csv_file(self, file_path):
        return (os.path.join(path, filename) for path, dir_, filenames in os.walk(file_path) for filename in filenames)
    # csv 파일로 데이터 저장
    def save2csv(self, save_data, save_file_path):
        # 폴더가 없을 시 폴더 생성
        dir_ = save_file_path[:save_file_path.rfind('/')]
        if not os.path.exists(dir_):
            os.mkdir(dir_)
        df = pd.DataFrame(sorted(save_data.items(), key=lambda x : x[1], reverse=True), columns=['word', 'count'])
        # 파일 저장
        df.to_csv(save_file_path, index=False, mode='w', encoding=self.encoding)

        print(f'save file at {save_file_path}')

    # 데이터 파일 읽기
    # 1안은 특정 컬럼의 데이터만 가져오기
    # 2안은 전체 데이터를 가져와서 run() 함수에서 컬럼으로 데이터 뽑기. 2안으로 채택
    def read_data_file(self, file_path):
        return pd.read_csv(file_path, encoding=self.encoding)
    
    def divide_text(self, data):
        if data != 'nan':
            # 텍스트 전처리 과정
            # texts = self.okt.morphs(data)
            texts = self.okt.pos(data)
        else:
            print('None data')
            texts = None
        return texts

    def pre_processing(self, datas, pos, stopwords, thesaurus):
        results = dict()
        for data in datas:
            texts = self.divide_text(data)
            # 메모리를 더 쓰고 속도를 빠르게 하자.
            for text in texts:
                # text 길이가 2 이상, 특정 형태소가 아니고, 불용어가 아니라면
                if len(text[0]) > 1 and text[1] not in pos and text not in stopwords:
                    # 시소러스 처리 해야 하는 코드 입력
                    # if text not in thesaurus:
                    # wid = vDict.getIdOrAdd(text)
                    # wcount[wid] = wcount.get(wid, 0) + 1
                    results[text[0]] = results.get(text[0], 0) + 1
            # for wid in wcount:
                # self.vDictFiltered.getIdOrAdd(self.vDict.getWord(wid))
                # results[vDict.getWord(wid)[0]] = wcount[wid]
        return results
        
    async def fetch(self, file_path, data_column='text', pos=['Josa', 'Suffix', 'Punctuation'],
            stopwords_file_path='./datasets/before/stopwords_thesaurus/stopwords.csv',
            thesaurus_path='./datasets/before/stopwords_thesaurus/thesaurus.csv'
            ):
        # 스레드 시작점
        print(f'Thread name : {threading.current_thread().getName()} Start!')

        # 불용어, 유의어 파일 읽기
        stopwords = self.read_data_file(stopwords_file_path)
        thesaurus = self.read_data_file(thesaurus_path)

        vDict = VocabDict()
        wcount = dict()
        # 데이터 파일 읽기
        try:
            # 파일을 multi process로 읽고
            with ProcessPoolExecutor(max_workers=min(32, self.cpu_count+4)) as executor:
                datas = executor.submit(self.read_data_file, file_path)[data_column]
            # 데이터 비동기 처리
            
                # future = await loop.run_in_executor(executor, )
            # datas = self.read_data_file(file_path)[data_column]
            # nan 데이터 처리 #
            # 1안은 제거. 2안은 별점을 토대로 1, 3 ,5를 기준으로 싫다 보통 좋다로 나누기.
            # 댓글 없는 행은 아예 drop했음
            datas = datas.dropna()
            print('##############################################################')
            # 여기서 데이터 분할 후 pre_processing 함수에서 데이터 넘겨주고 multiprocessing 으로 실행
            # 2차원 배열로 (댓글 전체 개수, 한 댓글에서 형태소 분할한 리스트) 모양으로 되어있음.
            # 한 파일에 있는 모든 데이터 자료구조에 저장
            # 데이터 cpu 개수만큼 혹은 cpu 개수 + 1 만큼 쪼개기
            divide = len(datas) // self.cpu_count
            datas_group = [datas[i*divide:(i+1)+divide] for i in range(divide)]
            if datas[divide*self.cpu_count:] != list():
                datas_group.append(datas[divide*self.cpu_count:])

            with ProcessPoolExecutor(max_workers=min(32, self.cpu_count+4)) as executor:
                future = [executor.submit(self.pre_processing, datas, pos, stopwords, thesaurus) for datas in datas_group]

                pass
            # a = [Process(target=self.pre_processing, args=(datas, pos, stopwords, thesaurus)) for datas in datas_group]

            results = self.pre_processing(datas, pos, stopwords, thesaurus)
            # 파일 저장
            save_file_path = self.change_dir(file_path)
            self.save2csv(results, save_file_path,)
        except:
            print(f'there is no data file at {file_path}')
        
        # 스레드 끝나는 지점
        print(f'Thread name : {threading.current_thread().getName()} Done!')

    async def run(self, ):
        futures = [asyncio.ensure_future(self.fetch(file_path) for file_path in self.read_csv_file(self.read_dir_path))]
        await asyncio.gather(*futures)
        print('Done!')

    # 자연어 처리
    # 1안 여러개의 파일을 비동기로 읽어서 데이터 처리.
    # 2안 : 1안 이후, 읽어들인 파일에서 멀티 프로세싱 및 병렬 계산 처리
    def run(self, data_column='text', pos=['Josa', 'Suffix', 'Punctuation'],
            stopwords_file_path='./datasets/before/stopwords_thesaurus/stopwords.csv',
            thesaurus_path='./datasets/before/stopwords_thesaurus/thesaurus.csv'
            ):
        # 불용어, 유의어 파일 읽기
        stopwords = self.read_data_file(stopwords_file_path)
        thesaurus = self.read_data_file(thesaurus_path)
        
        for file_path in self.read_csv_file(self.read_dir_path):
            vDict = VocabDict()
            wcount = dict()
            # 데이터 파일 읽기
            try:
                datas = self.read_data_file(file_path)[data_column]
            except:
                print(f'there is no data file at {file_path}')
                break
            # nan 데이터 처리 #
            # 1안은 제거. 2안은 별점을 토대로 1, 3 ,5를 기준으로 싫다 보통 좋다로 나누기.
            # 댓글 없는 행은 아예 drop했음
            datas = datas.dropna()
            print('##############################################################')
            results = dict()
            # 한 파일에 있는 모든 데이터 자료구조에 저장
            for data in datas:
                texts = self.divide_text(data)
                # 메모리를 더 쓰고 속도를 빠르게 하자.
                for text in texts:
                    # text 길이가 2 이상, 특정 형태소가 아니고, 불용어가 아니라면
                    if len(text[0]) > 1 and text[1] not in pos and text not in stopwords:
                        # 시소러스 처리 해야 하는 코드 입력
                        # if text not in thesaurus:
                        wid = vDict.getIdOrAdd(text)
                        wcount[wid] = wcount.get(wid, 0) + 1
                        # results[text[0]] = results.get(text[0], 0) + 1
                for wid in wcount:
                    # self.vDictFiltered.getIdOrAdd(self.vDict.getWord(wid))
                    results[vDict.getWord(wid)[0]] = wcount[wid]
            # 파일 저장
            save_file_path = self.change_dir(file_path)
            self.save2csv(results, save_file_path,)

if __name__ == '__main__':

    dir_path = './datasets/before/'
    today_date = str(datetime.date.today())
    dir_path = os.path.join(dir_path, today_date)
    start = timeit.default_timer()
    nlp = NLP(dir_path)
    nlp.run()
    end = timeit.default_timer() - start
    print(f'running time : {end}')