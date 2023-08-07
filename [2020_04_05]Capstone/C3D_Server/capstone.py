import os
import c3d
import numpy as np
import random
import io

import pprint
import pandas as pd

# 1. 소실된 점 복구.
class Data_Restoration:
    def run(self, data, no_data_point=None):
        
        result_data, no_data_point = self.data_restoration(data, no_data_point)
        
        return result_data, no_data_point

    # 데이터 복구
    def data_restoration(self, data, no_data_point):
        # 원본 데이터에서 null 위치 체크
        if no_data_point is None:
            no_data_point =  self.__data_restoration_no_data_check__(data)
        # 데이터는 꽉 차있을 시.
        if no_data_point == list():
            return data, no_data_point
        
        # 전 값, 다음 값, 프레임, 마커 위치 result에 반환.
        datalists =  self.__data_restoration_result__(no_data_point, data)
        # 예측값을 넣어서 result_data로 반환
        result_data =  self.__data_restoration_predict__(datalists, data)

        return result_data, no_data_point

    # 데이터에 null( 값이 들어 있지 않는 부분) 이 어디인지 체크
    def __data_restoration_no_data_check__(self, data):
        no_find = [0., 0., 0., -1., -1.]
        check = np.where(data == no_find)
        no_data_point = set(zip(check[0], check[1]))
        
        no_data_point = sorted(list(no_data_point))

        return no_data_point

    # 전 값, 다음 값, 프레임, 마커 위치 datalists에 반환.
    def __data_restoration_result__(self, no_data_point, data):
        result = dict()
        datalists = list()
        # print(no_data)
        
        for frame, marker in no_data_point:
            
            if (frame - 1, marker) not in no_data_point:
                result[marker] = dict()
                result[marker]['before_data'] = (data[frame-1][marker], frame-1, marker)
                
            if (frame + 1, marker) not in no_data_point:
                try:
                    result[marker]['after_data'] = (data[frame+1][marker], frame+1, marker)
                    datalists.append((result[marker]['before_data'], result[marker]['after_data']))
                except:
                    
                    before_data, before_frame, _ = result[marker]['before_data']
                    result[marker]['after_data'] = (before_data, frame+1, marker)
                    result[marker]['before_data'] = (data[before_frame-1][marker], before_frame, marker)
                    datalists.append((result[marker]['before_data'], result[marker]['after_data']))
        return datalists

    # 예측값을 넣어서 result_data로 반환
    def __data_restoration_predict__(self, datalists, data):
        for datalist in datalists:
            
            before_data, after_data = datalist[0], datalist[1]
            # time 은 frame 차이.
            time = after_data[1] - before_data[1]
            predict_points =  self.predict_before_after(before_data[0], after_data[0], time)
            
            # mark = 마커 번호
            mark = after_data[2]
            # after_data frame 번호를 after_data frame 이 아니라 after_data 전 프레임으로 넣었으므로
            for i, frame in enumerate(range(before_data[1]+1, after_data[1], 1)):
                data[frame][mark] = predict_points[i]
            
        return data

    # 빈 값일 때
    # 이전 값과 다음 값으로 데이터 예측
    def predict_before_after(self, before_point, after_point, time):
        # 공차
        tolerance = (after_point - before_point) / (time)
        # before값에 등차 더한것 리스트. 등차수열.
        predict_point = [np.ravel(before_point + tolerance*i) for i in range(1, time)]
        
        predict_point = np.array(predict_point)
        
        return predict_point

# 2. 각 점들이 잘못되어있는지 확인
# 이전프레임에서 갑자기 너무 많이 움직이거나 방향이 변경됐는지 확인
# 값이 있는데 잘못된 값일 때
class Data_Check:
    def __init__(self, labels, over_ratio= 1.01, down_ratio=0.09, distance_ratio=0.015,):
        self.over_ratio=over_ratio
        self.down_ratio=down_ratio
        self.distance_ratio=distance_ratio
        self.labels = labels

    def run(self, data, no_data_point):

        result_data, no_point_data =  self.sphere_check(data, no_data_point, self.over_ratio, self.down_ratio)
        return result_data, no_point_data

    # 2안 양 옆 두 구에서 평면 방정식을 이용해서 그 안에 값을 앞 뒤 등차수열 값으로.
    def sphere_check(self, data, no_data_point, over_ratio, down_ratio,):
        # sphere left right point에 data, label 집어넣기.
        left_data, right_data, weird_data, left_sphere_radius, right_sphere_radius, frame_num = \
             self.__sphere_left_right_point__(data, self.labels)
        
        if len(left_data) == 0 :
            return data, no_data_point
        
        # left_side == 두 구의 방정식을 뺀 좌변
        # left_side = right_data*2 - left_data*2 - left_data*left_data + right_data*right_data. 두 항을 우변으로 옮김
        left_side = (right_data - left_data)*2
        # right_side == 두 구의 방정식을 뺀 우변

        right_side = left_sphere_radius*left_sphere_radius - right_sphere_radius*right_sphere_radius \
                    + np.sum(right_data*right_data - left_data*left_data, axis=1)

        # right_side = right_sphere_radius*right_sphere_radius - left_sphere_radius*left_sphere_radius \
        #             + np.sum(left_data*left_data - right_data*right_data, axis=1)

        weird_result = np.sum(left_side * weird_data, axis=1)
        
        ratio = weird_result/right_side
        
        ratio = np.reshape(ratio, (frame_num, ratio.shape[0]//frame_num , 1))
        
        # 새로 시도해본 방식
        up_down_ratio = np.array([1.,])
        dt = 0.000001
        find_wrong_data = np.where(up_down_ratio != ratio)
        # find_wrong_data = np.where((up_down_ratio - dt >= ratio) | (up_down_ratio + dt <= ratio))
        
        find_wrong_data = zip(find_wrong_data[0], find_wrong_data[1])

        for frame, mark in find_wrong_data:
            data[frame][mark] = np.array([0., 0., 0., -1., -1.])

        data_restoration = Data_Restoration()
        
        return  data_restoration.run(data)

    def __sphere_left_right_point__(self, data, labels):
        # data, label 받아.
        label = [mark.rstrip() for mark in labels]
        weird_data_list = [
                            'LFHD', 'LBHD', 'RFHD', 'RBHD', 'C7',
                            'CLAV', 'RBAK','T10', 'STRN', 'RHSO',
                            'RUPA', 'RELB', 'RFRM', 'RWRB', 'RWRA',
                            'RFIN', 'RPSI', 'RASI', 'RTHI', 'RKNE',
                            'RTIB', 'RANK', 'RHEE',
                            'LSHO', 'LUPA', 'LELB', 'LFRM', 'LWRB',
                            'LWRA', 'LFIN', 'LPSI', 'LASI', 'LTHI',
                            'LKNE', 'LTIB', 'LANK', 'LHEE',
                            ]

        left_data_list = [
                            'RFHD', 'LBHD', 'LFHD', 'LBHD', 'LFHD',
                            'LSHO', 'T10', 'STRN', 'T10', 'CLAV',
                            'RSHO', 'RUPA', 'RELB', 'RFRM', 'RWRB',
                            'RWRA', 'LPSI', 'LASI', 'RASI', 'RTHI',
                            'RKNE', 'RTIB', 'RANK',
                            'CLAV', 'LSHO', 'LUPA', 'LELB', 'LFRM',
                            'LWRB', 'LWRA', 'RPSI', 'RASI', 'LASI',
                            'LTHI', 'LKNE', 'LTIB', 'LANK',
                            ]

        right_data_list = [
                            'C7', 'C7' 'C7', 'C7', 'RFHD',
                            'RSHO', 'CLAV', 'CLAV', 'CLAV', 'RUPA',
                            'RELB', 'RFRM', 'RWRB', 'RWRA', 'RFIN',
                            'RWRB', 'RASI', 'RPSI', 'RKNE', 'RTTB',
                            'RANK', 'RHEE', 'RTOE',
                            'LUPA', 'LELB', 'LFRM', 'LWRB', 'LWRA',
                            'LFIN', 'LWRB', 'LASI', 'LPSI', 'LKNE',
                            'LTIB', 'LANK', 'LHEE', 'LTOE',
                            ]

        label_mark_index = dict()
        def label_input(label_data):
            for weird, left, right in label_data:
                try:
                    label_mark_index[label.index(weird)] = {'left' : label.index(left), 'right': label.index(right)}
                except:
                    
                    pass
        label_input(zip(weird_data_list, left_data_list, right_data_list))

        mark_val = list(label_mark_index.values())
        frame_num = len(data)
        
        # 이전에 사용했던 방법
        # left_data = [data[frame][mark-1] for frame, mark in no_data_point if mark !=0 and mark != limit]
        # 여기를 조금 변경하자. 1차원 말고 2차원으로 만들면 절대 안돼. 프레임도 계산하게 되니까.
        left_data = [data[frame][mark['left']] for mark in mark_val for frame in range(frame_num)]
        right_data = [data[frame][mark['right']] for mark in mark_val for frame in range(frame_num)]
        weird_data = [data[frame][mark] for mark in label_mark_index for frame in range(frame_num)]

        left_data = np.array(left_data)
        right_data = np.array(right_data)
        weird_data = np.array(weird_data)

        left_sphere_radius =  self.calc_distance(left_data, weird_data)
        right_sphere_radius =  self.calc_distance(right_data, weird_data)

        left_sphere_radius = np.array(left_sphere_radius)
        right_sphere_radius = np.array(right_sphere_radius)
        
        return left_data, right_data, weird_data, left_sphere_radius, right_sphere_radius, frame_num

    # 두 점 사이의 거리 계산.
    def calc_distance(self, before_point, present_point):

        distance = before_point - present_point
        distance *= distance
        # 한꺼번에 넣었을 때,
        try:
            distance = np.sum(distance, axis=1)
        except Exception as e:
            # 값을 하나씩 넣었을 때, 변경된 데이터 전송됐을 때.
            try:
                distance = np.sum(distance, axis=0)
            except Exception as e:
                print(e)

        distance = np.sqrt(distance)
        return distance

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
        random_number = int(frame*mark * self.err_percentage * 3) # 3은 x, y z 세개
        
        # 총 수정된 데이터 (frame, mark)
        modified_data_num = {(random.randint(1, frame), random.randint(0, mark)) for _ in range(random_number)}
        
        # random_len_random_data = random.randint(0, len(modified_data_num))
        print(f'min_data = {np.min(data[data>-1.0])}, max_data = {np.max(data)}')
        random_len_random_data = len(modified_data_num)//2

        if pattern == 0:
            # 데이터 소실, 변경 동시에 작업.
            for i, (f, m) in enumerate(modified_data_num):
                if i > random_len_random_data:
                    
                    data[f][m] = np.array([random.uniform(-1, 2), random.uniform(-1, 2), random.uniform(-1, 2), 0., 0.])
                else:
                    data[f][m] = np.array([0., 0., 0., -1., -1.])
        elif pattern == 1:
            # 데이터 소실만
            for i, (f, m) in enumerate(modified_data_num):
                data[f][m] = np.array([0., 0., 0., -1., -1.])
        elif pattern == 2:
            # 데이터 변경만
            for i, (f, m) in enumerate(modified_data_num):
                data[f][m] = np.array([random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), 0., 0.])
            

        return data, len(modified_data_num)

# 데이터 읽고 쓰기
class Data_Read_Write:
    '''
    over_ratio, down_ratio = 구의 방정식을 이용해서 해당 좌표 평면 비스므리하게 없으면 오류.

    distance_ratio = 거리가 0.15m 이상 벌어지면 오류.
    '''
    def __init__(self, dir_path, over_ratio=1.25, down_ratio=0.75, distance_ratio=1.5, ):
        self.dir_path = dir_path
        self.over_ratio = over_ratio
        self.down_ratio = down_ratio
        self.distance_ratio = distance_ratio
        self.point_labels = dict()
        
    # 데이터 읽기
    def read_data(self, file_path, ):
        with open(file_path, 'rb') as hd:
            reader = c3d.Reader(hd)
            # 한 프레임마다
            # self.point_labels[file_path] = reader.point_labels

            labels = reader.point_labels
            
            # 전체 데이터를 행렬로 바꿈
            origin_data = [(i, points, analog) for (i, points, analog) in reader.read_frames()]
            data = [points for (i, points, analog) in origin_data]
            analog_data = [analog for (i, points, analog) in origin_data]

            # data = [points for (i, points, analog) in reader.read_frames()]
            
            analog_data = np.array(analog_data)
            data = np.array(data)

        return data, analog_data, labels

    # 데이터 쓰기
    # c3d 파일로는 데이터를 저장 못할것 같고. db나 csv 파일에 따로 저장해야할 것 같음
    def write_c3d(self, data, analog_data, file_name):
        # 파일 이름 적는 곳
        dir_name = file_name[:file_name.rfind('/')]
        file_name = file_name[file_name.rfind('/'):]

        dir_name = dir_name.replace('before', 'after')
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_name = file_name.replace('.c3d', '_modified.c3d')
        file_name = dir_name + file_name

        # 파일 쓰기
        print(f'write file at : {file_name}')
        print('********************************************************************************************************')
        writer = c3d.Writer()

        for i in range(data.shape[0]):
            # writer.add_frames([(data[i, :], analog_data[i, :])])
            # writer.add_frames([(data[i], analog_data[i])])
            writer.add_frames([(-data[i], np.array([[]]))])
            # writer.add_frames([(data[i, :], np.array([[]]))])
        
        with open(file_name, 'wb') as h:
            writer.write(h)

        # c3d 파일 csv로 변환
        self.c3d2csv(data, file_name)

        return file_name

    # c3d 파일 csv 파일로 변환. analog 데이터는 변환하지 않았음.
    def c3d2csv(self, data, file_name):
        # 파일 이름 csv로 변환
        file_name = file_name.replace('.c3d', '.csv')
        data = data.copy()
        # 데이터가 x, y, z 순으로 들어있지 않고 x, z, y 순으로 들어있어서 이렇게 적었음.
        # 올바르게 들어가 있다면, x, y, z 순서대로 넣으면 됨.
        data = np.array([[[x, z, y] for x, y, z, err, cam in frame_data] for frame_data in data])
        # 데이터 모양 구하기
        frame, mark, point = data.shape
        # 데이터 형식 변환
        data = data.reshape((frame, mark*point))
        # 데이터 프레임 생성
        csv_data = pd.DataFrame(data)
        # csv로 저장, header = column 쓰냐 안쓰냐.
        csv_data.to_csv(file_name, sep=',', mode='w', header=False)

        return file_name
        
    # 실행
    def run(self, write_file=False):
        # 파일이 아니면 == 폴더 이면.
        if self.dir_path[-4] != '.':
            paths = (f'{path}/{filename}' for path, _, filenames in os.walk(self.dir_path) for filename in filenames)
            datas = [( self.read_data(path, ), path) for path in paths]
            for (data, analog_data, labels), file_path in datas:
                print(file_path)
                # result, no_data_point = self.data_restore(data, labels)
                # self.print_percentage(data, result, no_data_point)

                if write_file:
                    # self.write_c3d(result, analog_data, file_path)
                    self.write_c3d(data, analog_data, file_path)
                return file_path
        # 파일이면
        else:
            print(self.dir_path)
            data, analog_data, labels = self.read_data(self.dir_path, )
            result, no_data_point = self.data_restore(data, labels)
            self.print_percentage(data, result, no_data_point)

            if write_file:
                self.write_c3d(result, analog_data, self.dir_path)
            return self.dir_path

    def data_restore(self, data, labels):
        # 데이터 복원
        data_restoration = Data_Restoration()
        # 데이터 검수 및 복원
        data_check = Data_Check(labels, over_ratio=self.over_ratio, down_ratio=self.down_ratio, distance_ratio=self.distance_ratio,)
        # before_no_data_point=고치기 전 이상한 곳 갯수
        
        data_restore, before_no_data_point =  data_restoration.run(data)
        
        # no_data_point=값이 이상한 곳. 못고친 곳. 얘를어쩌지? 이건 다시 수정해도 그대로야.
        # data_restore, no_data_point =  data_check.run(data_restore, before_no_data_point)
        
        # return data_restore, no_data_point
        return data_restore, before_no_data_point

    def print_percentage(self, data, data_restore, before_no_data_point):
        before_weird = len(before_no_data_point)
        print(f'before the number of weird data = {before_weird}')
        # 고친 후 이상한 곳 갯수
        check = data - data_restore
        
        ratio = np.array([0.1, 0.1, 0.1, 0., 0.])
        ratio *= 10
        find = np.where((check > ratio) | (check < -ratio))

        weird_data_point = list(set(zip(find[0], find[1])))
        weird_data_point = sorted(weird_data_point)
        
        after_weird = len(weird_data_point)
        print(f'after the number of weird data = {after_weird}')
        if before_weird == 0:
            print('there is no weird data')
            print('********************************************************************************************************')
        else:
            print(f'correct percentage : {(before_weird-after_weird)/before_weird * 100:0.2f}%')
            print('********************************************************************************************************')

class Percentage_of_Correction:
    def __init__(self, path, err_percentage=0.9):
        self.path = path
        self.err_percentage = err_percentage

    def run(self, write_file=False):
        # 데이터 읽음
        read_write = Data_Read_Write(self.path)
        # data_check = Data_Check(labels=read_write.labels)
        test_generate = Data_Test_Generate(self.path, self.err_percentage)
        # 실제 데이터
        origin_data, analog_data, labels = read_write.read_data(self.path)

        # 테스트 데이터 생성
        # 0은 혼합, 1은 소실만, 2는 위치 변경만
        test_data, modified_data_num = test_generate.run(pattern=1)
        # a number of 복수 = 복수, the number of 복수 = 단수
        #test_data2를 test_data로 변경
        test_data2, no_data_point = read_write.data_restore(test_data.copy(), labels)
        read_write.print_percentage(origin_data, test_data2, no_data_point)
        
        # check랑 where 조건문 바꿔야 함
        check = origin_data - test_data2
        
        # find 조건문을 바꿔야함 이거 어떻게 해야할까
        ratio = np.array([0.1, 0.1, 0.1, 0., 0.])
        ratio *= .1
        
        find = np.where((check > ratio) | (check < -ratio))
        
        # 뭐가 더 빠를까... 조건문이냐 함수냐...
        # check = abs(origin_data - test_data2)
        
        weird_data_point = list(set(zip(find[0], find[1])))
        weird_data_point = sorted(weird_data_point)
        
        after_result = len(weird_data_point)
        print(f'modified_data_num : {modified_data_num}, test : {after_result}')
        if modified_data_num == 0:
            print('there is no modified_data')
            print('********************************************************************************************************')
        else:
            print(f'correct percentage = { (modified_data_num-after_result)/modified_data_num * 100:0.2f}%')
            print('********************************************************************************************************')

        if write_file:
            # self.write_c3d(origin_data)
            # 원본
            self.write_c3d(origin_data, analog_data)
            # 테스트 데이터
            self.write_c3d(test_data, analog_data)
            # 복원 데이터
            self.write_c3d(test_data2, analog_data)
        # 데이터 이상한곳 출력해보기
        # for frame, mark in weird_data_point:
        #     print(f'here : {check[frame][mark]}')
        return origin_data, test_data, test_data2
    def write_c3d(self, data, analog_data):
        # 파일 이름 적는 곳
        dir_name = self.path[:self.path.rfind('/')]
        file_name = self.path[self.path.rfind('/'):]
        try:
            dir_name = dir_name.replace('before', 'after')
        except:
            pass
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_name = file_name.replace('.c3d', '_modified.c3d')
        file_name = dir_name + file_name
        self.path = file_name

        if os.path.exists(file_name):
            file_name = file_name.replace('.c3d', '_modified.c3d')
            self.path = file_name

        # 파일 쓰기
        print(f'write file at : {file_name}')
        print('********************************************************************************************************')
        writer = c3d.Writer()
        for i in range(data.shape[0]):
            # writer.add_frames([(data[i, :], analog_data[i, :])])
            writer.add_frames([(-data[i], np.array([[]]))])
        
        with open(file_name, 'wb') as h:
            writer.write(h)

        # os.system(f'python ./my_workspace/Univ/4-1/Capstone/c3d2csv.py {self.path}')
        self.c3d2csv(data, file_name)

        return file_name

    def c3d2csv(self, data, file_name):
        # 파일 이름 csv로 변환
        file_name = file_name.replace('.c3d', '.csv')
        # 원본은 다 -가 붙어있었지만, 안드로이드에서 읽을때 -가 붙어야 해서 - 붙였음
        data = data.copy()
        data = np.array([[[x, z, y] for x, y, z, err, cam in frame_data] for frame_data in data])
        # 데이터 모양 구하기
        frame, mark, point = data.shape
        # 데이터 형식 변환
        data = data.reshape((frame, mark*point))
        # 데이터 프레임 생성
        csv_data = pd.DataFrame(data)
        # csv로 저장, header = column 쓰냐 안쓰냐.
        csv_data.to_csv(file_name, sep=',', mode='w', header=False)
        

if __name__ == "__main__":

    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/'
    dir_path = 'my_workspace/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'my_workspace/datasets/after/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/'
    # data_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'

    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/Sample00_test/'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/demo/'
    # dir_path = 'my_workspace/datasets/after/[2020_03_12]Auto_Marking/'
    asdf = 'my_workspace/datasets/before/2020/[2020_03_12]Auto_Marking/Sample00_test/Motion Analysis Corporation/Walk1.c3d'
    raw_path = 'my_workspace/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_raw/Case1_raw.c3d'
    # test_data_path = 'my_workspace/datasets/after/[2020_06_11]Socket_Data/'
    # read_write = Data_Read_Write(asdf, )
    # write_file = True
    write_file = True
    # read_write.run(write_file=write_file)
    
    dir_path = 'my_workspace/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    edited_path = 'my_workspace/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_Edited'
    data_path = 'my_workspace/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_Edited/Case1_Edited.c3d'
    
    # read_write = Data_Read_Write(dir_path, )
    # read_write.run(write_file=write_file)
    percentage = Percentage_of_Correction(data_path, 0.8)
    percentage.run(write_file)

    # paths = (f'{path}/{filename}' for path, _, filenames in os.walk(edited_path) for filename in filenames)
    # for path in paths:
    #     print(path)
    #     percentage = Percentage_of_Correction(path, )
    #     origin_datas, test_data, modified_datas = percentage.run(True)
        # print(f'origin_datas : {origin_datas}\n modified_datas : {modified_datas}')
    # 05/24 LASI, RASI 와 같이 특정 마커 위치 넘기기.