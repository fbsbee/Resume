import pandas as pd
import numpy as np

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
 
vDict = VocabDict()
vDictFiltered = VocabDict()
wcount = {}  # 단어별 빈도가 저장될 dict
# 파일을 훑으며 단어별 빈도를 계산함

for line in open('input.txt'):
    words = list(set(line.split()))
    for w in words:
        wid = vDict.getIdOrAdd(w)
        wcount[wid] += wcount.get(wid, 0) + 1
 
for wid, num in wcount.items():
    if num < 10: continue
# 10회 이상 등장한 것들만 vDictFiltered에 저장함
    vDictFiltered.getIdOrAdd(vDict.getWord(wid))
############################################
# 위 는 단어 읽어와서 vDictFiltered에 넣으면 됨
 
vDict = None  # vDict에 할당된 메모리 반납
 
count = {}   #동시출현 빈도가 저장될 dict
# 파일을 다시 훑으며 동시출현빈도를 계산함
# pd.read()



for line in open('input.txt'):
    words = list(set(line.split()))   #단어별로 분리한 것을 set에 넣어 중복 제거하고, 다시 list로 변경
#vDictFiltered에 포함된 단어들에 대해서만 wid를 구함
    wids = list(filter(lambda wid : wid>=0, [vDictFiltered.getId(w) for w in words])) 
    for i, a in enumerate(wids):
        for b in wids[i+1:]:
            if a == b:
                continue   #같은 단어의 경우는 세지 않음
            if a > b:
                a, b = b, a   #A, B와 B, A가 다르게 세어지는것을 막기 위해 항상 a < b로 순서 고정
            count[a, b] = count.get((a, b), 0) + 1   #실제로 센다