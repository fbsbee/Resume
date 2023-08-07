import numpy as np
import pandas as pd
import os

# 불용어 및 시소러스 처리 클래스
class Pre_Processing:
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def save2csv(self, save_data, save_folder_path='./datasets/before/stopwords_thesaurus'):
        # 폴더가 없을 시 폴더 생성
        if not os.path.exists(save_folder_path):
            os.mkdir(save_folder_path)
        # 데이터 형식이 stopwords 형식이면 == list 형식이면
        if list().__class__ == save_data.__class__:
            file_path = self.save_stopwords(save_data)
        # 데이터 형식이 thesaurus 형식이면 == dict 형식이면
        elif dict().__class__ == save_data.__class__:
            file_path = self.save_thesaurus(save_data)
        else:
            print('do not input weird data.')
            return

        print(f'save file at {file_path}')

    # 불용어 저장
    def save_stopwords(self, save_data, file_name='stopwords.csv'):
        file_path = os.path.join(self.save_folder_path, file_name)
        if not os.path.exists(file_path):
            df = pd.DataFrame(data=save_data, columns=['stopwords'])
            df.to_csv(file_path, index=False, mode='w', encoding=self.encoding)
        else:
            # 원본 데이터 읽은 후
            origin_data = self.read_csv(file_path)
            # 데이터 평탄화
            origin_data = np.ravel(np.array(origin_data.values))
            # 존재하지 않는 데이터라면 저장
            save_data = [data for data in save_data if data not in origin_data]
            if len(save_data) > 0:
                print(f'{save_data} 데이터 저장')
                df = pd.DataFrame(data=save_data, columns=['stopwords'])
                df.to_csv(file_path, index=False, mode='a', encoding=self.encoding, header=False)
            else:
                print('데이터가 이미 존재합니다')
        
        return file_path

    # 동의어 저장
    def save_thesaurus(self, save_data, file_name = 'thesaurus.csv'):
        file_path = os.path.join(self.save_folder_path, file_name)
        # 파일이 존재하지 않으면 파일 생성
        if not os.path.exists(file_path):
            df = pd.DataFrame(data=save_data)
            print(df)
            df.to_csv(file_path, index=False, mode='w', encoding=self.encoding)
        # 파일이 존재한다면
        else:
            # 데이터 읽기
            origin_data = self.read_csv(file_path)

            # 새로 넣을 데이터 확인
            for k, v in save_data.items():
                try:
                    # 데이터가 있는지 체크 후 평탄화(1차원 배열로 변경)
                    # check_data = np.ravel(np.array(origin_data[k][origin_data[k].isin(v)].values))
                    input_data = np.ravel(np.array(origin_data[k].values))
                    input_data = [data for data in v if data not in input_data]
                except:
                    # 컬럼이 없다면 None으로 변경
                    input_data = None

                # 존재하지 않는 데이터라면
                if input_data is None:
                    # 새로운 데이터 프레임 생성 후
                    new_data = pd.DataFrame(data={k:v})
                    # 두 데이터 프레임 병합
                    concat_data = pd.concat([origin_data, new_data], axis=1)
                    print(concat_data)
                    # 데이터 저장
                    df = pd.DataFrame(data=concat_data, )
                    df.to_csv(file_path, index=False, mode='w', encoding=self.encoding,)

                # 기존에 데이터가 있고 새로운 데이터가 추가되었다면
                elif len(input_data) > 0:
                    # 새로운 데이터 프레임 생성 후
                    new_data = pd.DataFrame(data={k:input_data})
                    # 기존 데이터에서 nan값을 버린 후, dataframe 객체로 변환 한 다음 새로운 데이터와 병합
                    new_data = pd.concat([pd.DataFrame(origin_data[k].dropna()), new_data], axis=0, ignore_index=True)
                    # 기존 데이터에서 k 열 드랍
                    origin_data = origin_data.drop(k, axis=1)
                    # 드랍된 기존 데이터와 새로운 데이터 병합
                    concat_data = pd.concat([origin_data, new_data], axis=1,)
                    print(concat_data)
                    # 데이터 저장
                    df = pd.DataFrame(data=concat_data, )
                    df.to_csv(file_path, index=False, mode='w', encoding=self.encoding, )
                
                # 데이터가 있었다면
                else:
                    print('데이터가 이미 존재합니다')

        return file_path

    # 데이터 파일 읽기
    def read_csv(self, file_path):
        return pd.read_csv(file_path, encoding=self.encoding, )
    # 열 읽기
    def read_column(self, data, k):
        return data[k]
    # 열 드랍
    def drop_column(self, data, k):
        return data.drop(k, axis=1)
    # 여러 행 드랍하는 방법은 찾아봐야 함
    # 행 드랍
    def drop_row(self, data, v):
        return data.drop(v, axis=0)
        

if __name__ == "__main__":
    pp = Pre_Processing()
    # data = ['공원', 'ㅂㄹ', '19', 'ㄱㄱㄱㅂㄱㅂㄲㅂㄲ', 'ㅠㅠ', 'ㅏㅏ']
    data = {'좋아요' : ['좋습니다', '좋았어요', '좋은']}
    # data = {'좋아요' : ['좋았습니다']}
    # data = {'좋아요' : ['좋음']}
    # data = {'있습니다' : ['있는', '있어']}
    # data = {'있습니다' : ['있는', '있어', '있어요']}
    # data = {'제주' : ['제주도']}
    pp.save2csv(data, )

    ######################### 여러 행 드랍하는 방법 찾아봐야 함 ############################