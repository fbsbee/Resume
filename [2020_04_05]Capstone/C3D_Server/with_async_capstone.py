import os
import c3d
import numpy as np
import random
import asyncio

import pprint

# import pygame
# from pygame.locals import *
# from OpenGL.GL import *
# from OpenGL.GLU import *

# 1. 소실된 점 복구. 얘는 한번만 하면 되잖아.
class Data_Restoration:
    async def run(self, data, no_data_point=None):
        # args에 그게 들어가지 path가
        
        result_data, no_data_point = await self.data_restoration(data, no_data_point)
        
        return result_data, no_data_point

    # 데이터 복구
    async def data_restoration(self, data, no_data_point):
        # 원본 데이터에서 null 위치 체크
        if no_data_point is None:
            no_data_point = await self.__data_restoration_no_data_check__(data)
        # 데이터는 꽉 차있을 시.
        if no_data_point == list():
            return data, no_data_point
        
        # 전 값, 다음 값, 프레임, 마커 위치 result에 반환.
        datalists = await self.__data_restoration_result__(no_data_point, data)
        # 예측값을 넣어서 result_data로 반환
        result_data = await self.__data_restoration_predict__(datalists, data)

        return result_data, no_data_point

    # 데이터에 null( 값이 들어 있지 않는 부분) 이 어디인지 체크
    async def __data_restoration_no_data_check__(self, data):
        no_find = [0., 0., 0., -1., -1.]
        check = np.where(data == no_find)
        no_data_point = set(zip(check[0], check[1]))
        
        no_data_point = sorted(list(no_data_point))

        return no_data_point

    # 전 값, 다음 값, 프레임, 마커 위치 datalists에 반환.
    # random값 말고 평균값으로 바꾸면 되겠다.
    async def __data_restoration_result__(self, no_data_point, data):
        result = dict()
        datalists = list()
        # print(no_data)
        for frame, point in no_data_point:
            
            if (frame - 1, point) not in no_data_point:
                result[point] = dict()
                result[point]['before_data'] = (data[frame-1][point], frame-1, point)
                
            if (frame + 1, point) not in no_data_point:
                try:
                    result[point]['after_data'] = (data[frame+1][point], frame+1, point)
                    datalists.append((result[point]['before_data'], result[point]['after_data']))
                except:
                    # 1. 0, 0, 0, 0, 0 넣는거 고쳐야 함. 임시로 00000 넣었음. 근데 없던데... 큰일남 이거...
                    # 2. 0, 0, 0, 0, 0 넣는걸 임시로 before_data로 넣었음. 이것도 문제인데... 제일 큰일남 이거...
                    # 아니면 after_data를 넣으라고 할까? 이거 때문에 다 이상해지니까...

                    # print(f'You have to input data at last frame. \nframe : {frame}, point : {point}')

                    # raise IndexError(f'You have to input data at last frame. \nframe : {frame}, point : {point}')
                    # 여기 밑은 하지 말까 그냥
                    
                    before_data, before_frame, _ = result[point]['before_data']
                    result[point]['after_data'] = (before_data, frame+1, point)
                    # 이걸 추가 하냐 마느냐
                    result[point]['before_data'] = (data[before_frame-1][point], before_frame, point)
                    datalists.append((result[point]['before_data'], result[point]['after_data']))
                    # print('There is no more data \n')
        return datalists

    # 예측값을 넣어서 result_data로 반환
    async def __data_restoration_predict__(self, datalists, data):
        for datalist in datalists:
            
            before_data, after_data = datalist[0], datalist[1]
            # time 은 frame 차이.
            time = after_data[1] - before_data[1]
            predict_points = await self.predict_before_after(before_data[0], after_data[0], time)
            
            # mark = 마커 번호
            mark = after_data[2]
            # after_data frame 번호를 after_data frame 이 아니라 after_data 전 프레임으로 넣었으므로
            for i, frame in enumerate(range(before_data[1]+1, after_data[1], 1)):
                data[frame][mark] = predict_points[i]
            
        return data

    # 빈 값일 때
    # 이전 값과 다음 값으로 데이터 예측
    async def predict_before_after(self, before_point, after_point, time):
        # 공차
        tolerance = (after_point - before_point) / (time)
        # before값에 등차 더한것 리스트. 등차수열.
        predict_point = [np.ravel(before_point + tolerance*i) for i in range(1, time)]
        
        predict_point = np.array(predict_point)
        
        return predict_point

# 2. 각 점들이 잘못되어있는지 확인
# 이전프레임에서 갑자기 너무 많이 움직이거나 방향이 확 변경됐는지 이런거 확인
# 값이 있는데 잘못된 값일 때
# 이전 값과 그 이전 값 두개로 데이터 예측

# 얘도 한번만 해. 대신 run 함수 내에서 check_result가 []일때까지 while로 돌리던가, 
# sphere_check, distance_check 따로따로 내부에서 while로 돌리던가 
# 아니면 둘을 같이 하던가 해.
# distance_check는 random값을 어떻게 넣어주어야 할지 아직 생각이 안나.
class Data_Check:
    def __init__(self, labels, over_ratio= 1.01, down_ratio=0.09, distance_ratio=0.015,):
        self.over_ratio=over_ratio
        self.down_ratio=down_ratio
        self.distance_ratio=distance_ratio
        self.labels = labels

    async def run(self, data, no_data_point):

        result_data, no_point_data = await self.sphere_check(data, no_data_point, self.over_ratio, self.down_ratio)
        return result_data, no_point_data
        # if no_data_point != list():
        #     # data, label, over, down
        #     sphere_check_result = await self.sphere_check(data, no_data_point, self.over_ratio, self.down_ratio)
            
        #     return data, no_data_point
        # else:
        #     return data, no_data_point

    # 2안 양 옆 두 구에서 평면 방정식을 이용해서 그 안에 값을 앞 뒤 등차수열 값으로 넣어.
    async def sphere_check(self, data, no_data_point, over_ratio, down_ratio,):
        # sphere left right point에 data, label 집어넣기.
        left_data, right_data, weird_data, left_sphere_radius, right_sphere_radius, frame_num = \
            await self.__sphere_left_right_point__(data, self.labels)
        
        if len(left_data) == 0 :
            return data, no_data_point
        
        # left_side == 두 구의 방정식을 뺀 좌변
        # left_side = right_data*2 - left_data*2 - left_data*left_data + right_data*right_data. 두 항을 우변으로 옮김
        # left_side = right_data*2 - left_data*2
        left_side = (right_data - left_data)*2
        # right_side == 두 구의 방정식을 뺀 우변
        right_side = left_sphere_radius*left_sphere_radius - right_sphere_radius*right_sphere_radius \
                    + np.sum(right_data*right_data - left_data*left_data, axis=1)
        weird_result = np.sum(left_side * weird_data, axis=1)
        # print(f'{left_side} * [x, y, z] = {right_side}')
        # print(f'{np.sum(left_side * weird_data, axis=1)} = {right_side} ? ')
        
        # print(f'check : {np.array_equal(weird_result, right_side)}')
        ratio = weird_result/right_side
        
        # print(ratio.shape, frame_num, ratio.shape[0]//frame_num)
        ratio = np.reshape(ratio, (frame_num, ratio.shape[0]//frame_num , 1))
        
        # 새로 시도해본 방식
        up_down_ratio = np.array([1.,])
        dt = 0.000001
        find_wrong_data = np.where(up_down_ratio != ratio)
        # find_wrong_data = np.where((up_down_ratio - dt >= ratio) | (up_down_ratio + dt <= ratio))
        
        find_wrong_data = zip(find_wrong_data[0], find_wrong_data[1])
        # print('find_wrong_data len :', len(list(find_wrong_data)))

        for frame, mark in find_wrong_data:
            data[frame][mark] = np.array([0., 0., 0., -1., -1.])

        data_restoration = Data_Restoration()
        # result_data, no_point_data = await data_restoration.run(data, find_wrong_data)
        # print(f'no_point_data : {no_point_data}, \n find_wrong_data : {list(find_wrong_data)}')
        return await data_restoration.run(data)
        # 이전까지 해왔던 방식
        # find_wrong_data = np.where((ratio > over_ratio) | (ratio < down_ratio))[0]
        # find_wrong_data = np.where(ratio > [over_ratio])[0]
        # find_wrong_data = np.where(ratio < [down_ratio])[0]
        # find_wrong_data = np.where(ratio != 1.)[0]
        # result_wrong_point = [no_data_point[v] for v in find_wrong_data]

        
    # 이거 쓰면 느려지긴 할텐데 많을수록 조금 빨라지려나?
    async def input_rand_num(self, data, i, frame, mark, left_data, right_data):
        data[frame][mark] = random.uniform(left_data[i], right_data[i])

    # 이거 async로 해야할 것 같은데 5개 list에 하나씩 append하기에는 너무 아까워. 아직 못했어. 방법이 있을 낀데
    async def __sphere_left_right_point__(self, data, labels):
        # data, label 받아.
        label = [mark.rstrip() for mark in labels]
        weird_data_list = ['LFHD', 'LBHD', 'RFHD', 'RBHD', 'C7', \
                            'CLAV', 'RBAK','T10', 'STRN', 'RHSO', \
                            'RUPA', 'RELB', 'RFRM', 'RWRB', 'RWRA', \
                            'RFIN', 'RPSI', 'RASI', 'RTHI', 'RKNE', \
                            'RTIB', 'RANK', 'RHEE', \
                            'LSHO', 'LUPA', 'LELB', 'LFRM', 'LWRB', \
                            'LWRA', 'LFIN', 'LPSI', 'LASI', 'LTHI', \
                            'LKNE', 'LTIB', 'LANK', 'LHEE', 
                            ]

        left_data_list = ['RFHD', 'LBHD', 'LFHD', 'LBHD', 'LFHD', \
                            'LSHO', 'T10', 'STRN', 'T10', 'CLAV', \
                            'RSHO', 'RUPA', 'RELB', 'RFRM', 'RWRB', \
                            'RWRA', 'LPSI', 'LASI', 'RASI', 'RTHI', \
                            'RKNE', 'RTIB', 'RANK', \
                            'CLAV', 'LSHO', 'LUPA', 'LELB', 'LFRM', \
                            'LWRB', 'LWRA', 'RPSI', 'RASI', 'LASI', \
                            'LTHI', 'LKNE', 'LTIB', 'LANK',
                            ]

        right_data_list = ['C7', 'C7' 'C7', 'C7', 'RFHD', \
                            'RSHO', 'CLAV', 'CLAV', 'CLAV', 'RUPA', \
                            'RELB', 'RFRM', 'RWRB', 'RWRA', 'RFIN', \
                            'RWRB', 'RASI', 'RPSI', 'RKNE', 'RTTB', \
                            'RANK', 'RHEE', 'RTOE', \
                            'LUPA', 'LELB', 'LFRM', 'LWRB', 'LWRA', \
                            'LFIN', 'LWRB', 'LASI', 'LPSI', 'LKNE', \
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

        left_sphere_radius = await self.calc_distance(left_data, weird_data)
        right_sphere_radius = await self.calc_distance(right_data, weird_data)

        left_sphere_radius = np.array(left_sphere_radius)
        right_sphere_radius = np.array(right_sphere_radius)
        
        return left_data, right_data, weird_data, left_sphere_radius, right_sphere_radius, frame_num

    # 두 점 사이의 거리 계산.
    async def calc_distance(self, before_point, present_point):

        distance = before_point - present_point
        distance *= distance
        # 한꺼번에 넣었을 때,
        distance = np.sum(distance, axis=1)
        # 값을 하나씩 넣었을 때,
        # distance = np.sum(distance, axis=0)
        distance = np.sqrt(distance)
        return distance

# 데이터 테스트 하는 클래스
class Data_Test_Generate:
    
    def __init__(self, data_path, err_percentage):
        self.data_path = data_path
        self.err_percentage = err_percentage

    def run(self, ):
        data = self.read_data(self.data_path)
        data, modified_data_num = self.change_data(data)
        return data, modified_data_num

    def read_data(self, data_path):
        with open(data_path, 'rb') as hd:
            reader = c3d.Reader(hd)
            # 한 프레임마다
            data = [points for (i, points, analog) in reader.read_frames()]
            # 전체 데이터를 행렬로 바꿈
            data = np.array(data)

        return data

    def change_data(self, data, ):
        import random
        import time

        frame, mark, _ = data.shape
        frame , mark = frame - 1, mark -1
        # 변경할 데이터 갯수 frame * mark의 갯수
        # random_number = random.randint(1, frame*mark)
        random_number = int(frame*mark * self.err_percentage)
        
        # 총 수정된 데이터 (frame, mark)
        modified_data_num = {(random.randint(1, frame), random.randint(0, mark)) for _ in range(random_number)}
        
        # random_len_random_data = random.randint(0, len(modified_data_num))
        print(f'min_data = {np.min(data[data>-1.0])}, max_data = {np.max(data)}')
        random_len_random_data = len(modified_data_num)//2

        # 데이터 소실, 변경 동시에 작업.
        for i, (f, m) in enumerate(modified_data_num):
            if i > random_len_random_data:
                
                data[f][m] = np.array([random.uniform(-1, 2), random.uniform(-1, 2), random.uniform(-1, 2), 0., 0.])
            else:
                data[f][m] = np.array([0., 0., 0., -1., -1.])

        # 데이터 소실만
        # for i, (f, m) in enumerate(modified_data_num):
        #     data[f][m] = np.array([0., 0., 0., -1., -1.])

        # 데이터 변경만
        # for i, (f, m) in enumerate(modified_data_num):
        #     data[f][m] = np.array([random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), 0., 0.])
            

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
    async def read_data(self, file_path, ):
        with open(file_path, 'rb') as hd:
            reader = c3d.Reader(hd)
            # 한 프레임마다
            # self.point_labels[file_path] = reader.point_labels
            # pprint.pprint(f'labels : {self.point_labels}')
            labels = reader.point_labels
            # print(len(self.point_labels[file_path]))
            # data = [points for (i, points, analog) in reader.read_frames()]
            # 전체 데이터를 행렬로 바꿈
            # self.origin_data = [(i, points, analog) for (i, points, analog) in reader.read_frames()]
            # data = [points for (i, points, analog) in self.origin_data]
            # self.origin_data = np.array(self.origin_data)

            data = [points for (i, points, analog) in reader.read_frames()]
            
            data = np.array(data)

        return data, labels

    # 데이터 쓰기
    # c3d 파일로는 데이터를 저장 못할것 같고. db나 csv 파일에 따로 저장해야할 것 같음
    # analog 데이터를 수정 못함. 알 수가 없어
    async def write_c3d(self, data, file_name):
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
        for i in range(data.shape[1]):
            writer.add_frames([(data[:, i], np.array([[]]))])
        
        with open(file_name, 'wb') as h:
            writer.write(h)
        
    # 실행
    async def run(self, write_file=False):
        # 파일이 아니면 == 폴더 이면.
        if self.dir_path[-4] != '.':
            paths = (f'{path}/{filename}' for path, _, filenames in os.walk(self.dir_path) for filename in filenames)
            datas = [(await self.read_data(path, ), path) for path in paths]
            for (data, labels), file_path in datas:
                print(file_path)
                result, no_data_point = await self.data_restore(data, labels)
                await self.print_percentage(data, result, no_data_point)

                if write_file:
                    await self.write_c3d(result, file_path)
        # 파일이면
        else:
            print(self.dir_path)
            data, labels = await self.read_data(self.dir_path, )
            result, no_data_point = await self.data_restore(data, labels)
            await self.print_percentage(data, result, no_data_point)

            if write_file:
                await self.write_c3d(result, self.dir_path)

    async def data_restore(self, data, labels):
        # 데이터 복원
        data_restoration = Data_Restoration()
        # 데이터 검수
        data_check = Data_Check(labels, over_ratio=self.over_ratio, down_ratio=self.down_ratio, distance_ratio=self.distance_ratio,)
        # before_no_data_point=고치기 전 이상한 곳 갯수
        data_restore, before_no_data_point = await data_restoration.run(data)
        # no_data_point=값이 이상한 곳. 못고친 곳. 얘를어쩌지? 이건 다시 수정해도 그대로야.
        data_restore, no_data_point = await data_check.run(data_restore, before_no_data_point)
        
        return data_restore, no_data_point

    async def print_percentage(self, data, data_restore, before_no_data_point):
        before_weird = len(before_no_data_point)
        print(f'before the number of weird data = {before_weird}')
        # 고친 후 이상한 곳 갯수
        check = data - data_restore
        # print(before_no_data_point)
        
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
    def __init__(self, path, err_percentage=0.3):
        self.path = path
        self.err_percentage = err_percentage

    def run(self, ):
        # 데이터 읽음
        read_write = Data_Read_Write(self.path)
        # data_check = Data_Check(labels=read_write.labels)
        test_generate = Data_Test_Generate(self.path, self.err_percentage)
        # 실제 데이터
        origin_data, labels = asyncio.run(read_write.read_data(self.path))
        # 테스트 데이터 생성
        test_data, modified_data_num = test_generate.run()
        
        # a number of 복수 = 복수, the number of 복수 = 단수
        #test_data2를 test_data로 변경
        test_data2, no_data_point = asyncio.run(read_write.data_restore(test_data, labels))
        asyncio.run(read_write.print_percentage(origin_data, test_data2, no_data_point))
        # result, _는 없어도 됨. 내가 확인하고 싶어서.
        # result, _ = asyncio.run(data_check.run(test_data, no_data_point))

        # print(f'a == b ? : {np.array_equal(test_data, test_data2)}')
        # print(f'a == b ? : {np.array_equal(test_data2, result)}')
        
        # print(np.where(np.isnan(test_data2)==True))
        # check랑 where 조건문 바꿔야 함
        check = origin_data - test_data2
        
        # find 조건문을 바꿔야함 이거 어떻게 해야할까
        ratio = np.array([0.1, 0.1, 0.1, 0., 0.])
        ratio *= 10
        
        find = np.where((check > ratio) | (check < -ratio))
        
        # 뭐가 더 빠를까... 조건문이냐 함수냐...
        # check = abs(origin_data - test_data2)
        # find = np.where(check > [0.1, 0.1, 0.1, 0., 0.,])

        # find = np.where((check > [0.2, 0.2, 0.2, 0., 0.,]) | (check < [-0.2, -0.2, -0.2, 0., 0.,]))
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
        # 데이터 이상한곳 출력해보기
        # for frame, mark in weird_data_point:
        #     print(f'here : {check[frame][mark]}')
        return origin_data, test_data2

if __name__ == "__main__":

    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/'
    dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'my_workspace/datasets/after/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/'
    data_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/Case2_Edited.c3d'
    # data_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'

    dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/Sample00_test/'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/demo/'
    # dir_path = 'my_workspace/datasets/after/[2020_03_12]Auto_Marking/'
    edited_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/'

    # read_write = Data_Read_Write(dir_path, )
    # write_file = True
    # write_file = False
    # asyncio.run(read_write.run(write_file=write_file))
    
    # read_write = Data_Read_Write(data_path, )
    # asyncio.run(read_write.run())
    # percentage = Percentage_of_Correction(data_path)
    # percentage.run()

    paths = (f'{path}/{filename}' for path, _, filenames in os.walk(edited_path) for filename in filenames)
    for path in paths:
        print(path)
        percentage = Percentage_of_Correction(path, )
        origin_datas, modified_datas = percentage.run()

        # print(f'origin_datas : {origin_datas}\n modified_datas : {modified_datas}')

    # 05/24 LASI, RASI 와 같이 특정 마커 위치 넘기기.