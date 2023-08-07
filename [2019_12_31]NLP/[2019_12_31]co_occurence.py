import pandas as pd
import os
from multiprocessing import Process

class VocabDict:
# 단어에 고유 ID를 부여해주는 클래스
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
 
    def getId(self, word):
# 단어가 사전에 등록되어있는 경우 ID를 돌려주고
        if word in self.d:
            return self.d[word]
# 그렇지 않은 경우 -1을 돌려줌
        return -1
 
    def getWord(self, id):
        return self.w[id]
 
class Co_occur:
    '''
    init() -> word_dict_path = CF 개수 적어놓은 폴더 위치
              file_read_path = 크롤링하여 제목과 본문 적어놓은 폴더 위치
              write_path_dir = csv 파일 저장할 위치. default = './' (현재 python 실행 파일 위치)
              ----->>> 끝에 '/'나 '\\'를 붙여주어야 함. 

    run() -> noun_val = 단어 쌍에 넣을 상위 n개의 단어 추출
            count_val = 단어 쌍의 개수가 일정 이상인 단어 쌍만 추출
            save_file = True면 csv파일로 저장

    인용? 참고? 출처? 알고리즘은 그대로 가져다 사용 : https://bab2min.tistory.com/598
    '''
    def __init__(self, word_dict_path, file_read_path, write_path_dir='./'):
        self.word_dict_path = word_dict_path
        self.file_read_path = file_read_path
        self.write_path_dir = write_path_dir

        self.vDict = VocabDict()
        self.vDictFiltered = VocabDict()
        self.wcount = {}  # 단어별 빈도가 저장될 dict

    def run(self, noun_val=50, count_val=50, save_file=False):
        
        # CF에 있는 단어 쌍 vDictFiltered에 넣어둠
        for filepath in (path+filename for path, dir_, filenames in os.walk(self.word_dict_path) for filename in filenames):
            csv_file = pd.read_csv(filepath, encoding='utf8')
            nouns = csv_file['명사'].values[:noun_val]

            for w in nouns:
                wid = self.vDict.getIdOrAdd(w)
                self.wcount[wid] = self.wcount.get(wid, 0) + 1
            for wid in self.wcount:
                self.vDictFiltered.getIdOrAdd(self.vDict.getWord(wid))
                # print(vDictFiltered.getWord(wid))
        self.vDict = None

        # 한 게시글 당 동시출현빈도 계산
        for path, dir_, filenames in os.walk(self.file_read_path):
            for filename in filenames:
                csv_file = pd.read_csv(path+filename, encoding='utf8')
                
                titles = csv_file['제목'].values
                contexts = list(csv_file['내용'].values)
                count = {}   #동시출현 빈도가 저장될 dict

                # 단어별로 분리한 것을 set에 넣어 중복 제거하고, 다시 list로 변경
                for all in zip(titles, contexts):
                    words = set((str(all[0])+str(all[1])).split(' '))

                    #vDictFiltered에 포함된 단어들에 대해서만 wid를 구함
                    wids = list(filter(lambda wid : wid>=0, [self.vDictFiltered.getId(w) for w in words])) 
                    for i, a in enumerate(wids):
                        for b in wids[i+1:]:
                            if a == b:
                                continue   #같은 단어의 경우는 세지 않음
                            if a > b:
                                a, b = b, a   #A, B와 B, A가 다르게 세어지는것을 막기 위해 항상 a < b로 순서 고정
                            count[a, b] = count.get((a, b), 0) + 1   # 개수 카운트

                # 출력 및 저장 하는 곳
                result = {self.vDictFiltered.getWord(k[0])+':'+self.vDictFiltered.getWord(k[1]) : v for k, v in count.items() if v>=count_val}
                print(result)
                print(filename)
                
                if save_file:
                    co_occur_data = pd.DataFrame(sorted(result.items(), key=lambda x : x[1], reverse=True), columns=['단어쌍', '개수'])
                    co_occur_data.to_csv(f'{self.write_path_dir+filename}_pair.csv', sep='\t', mode='w')

if __name__ == "__main__":
    word_dict_path='datasets/after/[2019_11_22]NLP_real_Okt_test3/'
    file_read_path='datasets/before/[2019_11_22]NLP/'
    write_path_dir='datasets/after/[2019_12_30]NLP_Co_Occur/'
    
    # CF 파일은 상위 100개 까지만 불용어 정리 하였음
    data_mining = Co_occur(word_dict_path, file_read_path, write_path_dir)
    data_mining.run(noun_val=150, count_val=10 ,save_file=True)
    print('done')