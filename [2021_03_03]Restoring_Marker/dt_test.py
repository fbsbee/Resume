import numpy as np
import os
import c3d

# 데이터 테스트 하는 클래스
class Data_Test_Generate:
    
    def __init__(self, data_path, err_percentage):
        self.data_path = data_path 
        self.err_percentage = err_percentage

    def run(self, pattern=0):
        data = self.read_data(self.data_path)
        data, modified_data_num = self.change_data(data, pattern)
        return data, modified_data_num

    def read_data(self, data_path):
        with open(data_path, 'rb') as hd:
            reader = c3d.Reader(hd)
            # 한 프레임마다
            data = [points for (i, points, analog) in reader.read_frames()]
            # 전체 데이터를 행렬로 바꿈
            data = np.array(data)

        return data

    def change_data(self, data, pattern):
        import random
        import time

        frame, mark, _ = data.shape
        frame , mark = frame - 1, mark -1
        # 변경할 데이터 갯수 frame * mark의 갯수
        # random_number = int(frame*mark * self.err_percentage * 2) # 마지막의 *n은 변경할 데이터 개수를 조절하기 위한 값.

        # 이게 실제 개수와 입력한 퍼센티지 개수를 맞추기 위한 값이긴 한데, set으로 해버리니 random_number 개수가 줄 수 밖에 없음
        random_number = int(frame*mark * self.err_percentage)
        
        # 총 수정된 데이터 (frame, mark)
        # modified_data_num = {(random.randint(1, frame), random.randint(0, mark)) for _ in range(random_number)}
        modified_data_num = {(random.randint(1, frame), random.randint(0, mark)) for _ in range(random_number)}
        
        # random_len_random_data = random.randint(0, len(modified_data_num))
        # print(f'min_data = {np.min(data[data>-1.0])}, max_data = {np.max(data)}')
        print(f'min_data = {np.min(data)}, max_data = {np.max(data)}')
        min_arg = np.min(data)
        max_arg = np.max(data)
        random_len_random_data = len(modified_data_num)//2

        no_data = [0., 0., 0., -1., -1.]
        if pattern == 0:
            # 데이터 소실, 변경 동시에 작업.
            for i, (f, m) in enumerate(modified_data_num):
                if i > random_len_random_data:
                    data[f][m] = np.array([random.uniform(min_arg, max_arg), random.uniform(min_arg, max_arg), random.uniform(min_arg, max_arg), 0., 0.])
                else:
                    data[f][m] = np.array(no_data)
            
        elif pattern == 1:
            # 데이터 소실만
            for i, (f, m) in enumerate(modified_data_num):
                # print(f'before : {data[f][m]}')
                data[f][m] = np.array(no_data)
                # print(f'after : {data[f][m]}')
            
        elif pattern == 2:
            # 데이터 변경만
            for i, (f, m) in enumerate(modified_data_num):
                data[f][m] = np.array([random.uniform(min_arg, max_arg), random.uniform(min_arg, max_arg), random.uniform(min_arg, max_arg), 0., 0.])
            
        print(f'setting random_number = {random_number}, real change num = {i+1}, data shape : {data.shape}')
        print(f'{i/(frame*mark)*100:.2f}% data changed')
        
        return data, len(modified_data_num)