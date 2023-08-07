import math
import os
import c3d
import numpy as np
import asyncio

import pprint

# 1. 소실된 점 복구
class Data_Restoration:
    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        # args에 그게 들어가지 path가
        data = await self.func(self, *args, **kwargs)
    
        result_data, no_data_point = await self.data_restoration(data)

        return result_data, no_data_point

    async def data_restoration(self, data, ):
        # 원본 데이터에서 null 위치 체크
        no_data_point = await self.__data_restoration_no_data_check__(data)
        # 데이터는 꽉 차있을 시.
        if no_data_point == list():
            print('There is no null data')
            ################################ test용 coding ################################
            no_data_point = [(24, 5), (25, 5), (50, 2), (51, 2)]
            result = await self.__data_restoration_result__(no_data_point, data)
            result_data = await self.__data_restoration_predict__(result, data)
            ###############################################################################
            return data, no_data_point
        # 전 값, 다음 값, 프레임, 마커 위치 result에 반환.
        result = await self.__data_restoration_result__(no_data_point, data)
        # 예측값을 넣어서 result_data로 반환
        result_data = await self.__data_restoration_predict__(result, data)

        return result_data, no_data_point

    # 데이터에 null( 값이 들어 있지 않는 부분) 이 어디인지 체크
    async def __data_restoration_no_data_check__(self, data):
        no_find = [0., 0., 0., -1., -1.]
        check = np.where(data == no_find)
        no_data_point = set(zip(check[0], check[1]))
        
        no_data_point = sorted(list(no_data_point))

        return no_data_point

    # 전 값, 다음 값, 프레임, 마커 위치 datalists에 반환.
    async def __data_restoration_result__(self, no_data, data):
        result = dict()
        datalists = list()
        for frame, point in no_data:
            if (frame - 1, point) not in no_data:
                result[point] = dict()
                result[point]['before_data'] = (data[frame-1][point], frame-1, point)
                
            if (frame + 1, point) not in no_data:
                try:
                    result[point]['after_data'] = (data[frame+1][point], frame+1, point)
                    datalists.append((result[point]['before_data'], result[point]['after_data']))
                except IndexError as e:
                    # 1. 0, 0, 0, 0, 0 넣는거 고쳐야 함. 임시로 00000 넣었음. 근데 없던데... 큰일남 이거...
                    # 2. 0, 0, 0, 0, 0 넣는걸 임시로 before_data로 넣었음. 이것도 문제인데... 제일 큰일남 이거...
                    # 아니면 after_data를 넣으라고 할까? 이거 때문에 다 이상해지니까...

                    # print(f'You have to input data at last frame. \nframe : {frame}, point : {point}')

                    # raise IndexError(f'You have to input data at last frame. \nframe : {frame}, point : {point}')
                    # 여기 밑은 하지 말까 그냥
                    result[point]['after_data'] = (result[point]['before_data'][0], frame+1, point)
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
        # 등차
        allowance = (after_point - before_point) / (time)
        # before값에 등차 더한것 리스트
        predict_point = [np.ravel(before_point + allowance*i) for i in range(1, time)]
        
        predict_point = np.array(predict_point)
        
        return predict_point

class Data_Double_Restoration(Data_Restoration):
    async def __call__(self, *args, **kwargs):
        # args에 그게 들어가지 path가
        data, no_data_point = await self.func(*args, **kwargs)
    
        result_data, no_data_point = await self.data_restoration(data, no_data_point)

        return result_data, no_data_point

    async def data_restoration(self, data, no_data_point):
        # 데이터는 꽉 차있을 시.
        if no_data_point == list():
            print('There is no null data')
            return data, no_data_point
        # 전 값, 다음 값, 프레임, 마커 위치 result에 반환.
        result = await self.__data_restoration_result__(no_data_point, data)
        # 예측값을 넣어서 result_data로 반환
        result_data = await self.__data_restoration_predict__(result, data)
        
        return result_data, no_data_point

# 2. 각 점들이 잘못되어있는지 확인
# 이전프레임에서 갑자기 너무 많이 움직이거나 방향이 확 변경됐는지 이런거 확인
# 값이 있는데 잘못된 값일 때
# 이전 값과 그 이전 값 두개로 데이터 예측
class Data_Check:
    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        path, over_ratio, down_ratio, distance_ratio = args
        data, no_data_point = await self.func(*args, **kwargs)
        if no_data_point != list():
            sphere_check_result = await self.sphere_check(data, no_data_point, over_ratio, down_ratio)
            distance_check_result = await self.data_check(data, distance_ratio)
        else:
            sphere_check_result = []
            distance_check_result = await self.data_check(data, distance_ratio)

        check_result = sorted(list(set(sphere_check_result + distance_check_result)))
        
        return data, check_result

    async def data_check(self, data, distance_ratio,):
        # data 0 ~ n-1 까지 와 1 ~ n 까지 빼주고 거리 구함
        before_data = data[:len(data)-1]
        present_data = data[1:]

        distance = present_data - before_data
        distance *= distance
        # axis는 숫자가 작을 수록 제일 바깥(리스트)부터라고 보면 됨 axis = 0 x축, axis = 1 y축, axis =2 z축.
        distance = np.sum(distance, axis=2)
        distance = np.sqrt(distance)

        # 3차원으로 다시 바꿔줌
        distance = np.reshape(distance, distance.shape+(1,))
        # print(distance)

        # 0.015m? 이걸 좌표 distance로 어떻게 알아... 일단 임의값 넣어둠
        find_wrong_data = np.where(distance > distance_ratio)
        result_wrong_point = list(zip(find_wrong_data[0], find_wrong_data[1]))

        return result_wrong_point

    # 모든 오류들 이걸로 확인
    # 접평면의 방정식으로 x, y, z가 값이 맞는지 확인
    async def sphere_check(self, data, no_data_point, over_ratio, down_ratio,):
        left_data, right_data, predict_data, left_sphere_radius, right_sphere_radius = await self.__sphere_left_right_point__(data, no_data_point)
        # left_side == 두 구의 방정식을 뺀 좌변
        # left_side = right_data*2 - left_data*2 - left_data*left_data + right_data*right_data. 두 항을 우변으로 옮김
        left_side = right_data*2 - left_data*2
        
        # right_side == 두 구의 방정식을 뺀 우변
        right_side = left_sphere_radius*left_sphere_radius - right_sphere_radius*right_sphere_radius + np.sum(right_data*right_data - left_data*left_data, axis=1)
        predict_result = np.sum(left_side * predict_data, axis=1)
        # predict_result = np.reshape(predict_result, predict_result.shape+(1,))
        # print(f'{left_side} * [x, y, z] = {right_side}')

        # print(f'{np.sum(left_side * predict_data, axis=1)} = {right_side} ? ')

        # 1.25, 0.75 
        ratio = predict_result/right_side
        ratio = np.reshape(ratio, ratio.shape + (1,))
        find_wrong_data = np.where((ratio > over_ratio) | (ratio < down_ratio))
        find_wrong_data = find_wrong_data[0]
        result_wrong_point = [no_data_point[v] for v in find_wrong_data]
        
        return result_wrong_point

    # 이거 async로 해야할 것 같은데 5개 list에 하나씩 append하기에는 너무 아까워. 아직 못했어. 방법이 있을 낀데
    async def __sphere_left_right_point__(self, data, no_data_point):

        # for 문 하나에서 각각 append 하는것보다 하나씩 comprehension으로 감싸는게 2배 더 빠름...
        _, limit, _ = data.shape
        limit -= 1
        
        left_data = [data[frame][mark-1] for frame, mark in no_data_point if mark !=0 and mark != limit]
        right_data = [data[frame][mark+1] for frame, mark in no_data_point if mark !=0 and mark != limit]
        predict_data = [data[frame][mark] for frame, mark in no_data_point if mark !=0 and mark != limit]
        left_sphere_radius = [await self.calc_distance(data[0][mark+1], data[0][mark]) for _, mark in no_data_point if mark !=0 and mark != limit]
        right_sphere_radius = [await self.calc_distance(data[0][mark+1], data[0][mark]) for _, mark in no_data_point if mark !=0 and mark != limit]
        # 이거 두개는 많이 비효율적인것 같은데
        # left_sphere_radius = [await self.calc_distance(data[0][mark+1], data[0][mark]) for _, mark in no_data_point]
        # right_sphere_radius = [await self.calc_distance(data[0][mark+1], data[0][mark]) for _, mark in no_data_point]

        left_data = np.array(left_data)
        right_data = np.array(right_data)
        predict_data = np.array(predict_data)
        left_sphere_radius = np.array(left_sphere_radius)
        right_sphere_radius = np.array(right_sphere_radius)

        return left_data, right_data, predict_data, left_sphere_radius, right_sphere_radius

    # 두 점 사이의 거리 계산.
    async def calc_distance(self, before_point, present_point):
        distance = before_point - present_point
        distance *= distance
        distance = np.sum(distance)
        distance = math.sqrt(distance)
        return distance

# 데이터 테스트 하는 클래스
class Data_Test_Generate:
    
    def __init__(self, data_path):
        self.data_path = data_path

    def run(self, ):
        data = self.read_data(self.data_path)
        data = self.change_data(data)
        return data

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
        random_number = random.randint(0, frame*mark)
        
        random_data = {(random.randint(0, frame), random.randint(0, mark)) for _ in range(random_number)}

        random_len_random_data = random.randint(0, len(random_data))
        for i, (f, m) in enumerate(random_data):
            if i > random_len_random_data:
                data[f][m] = np.array([random.random(), random.random(), random.random(), 0., 0.])
            else:
                data[f][m] = np.array([0., 0., 0., -1., -1.])

        return data

# 데이터 읽고 쓰기
class Data_Read_Write:
    '''
    over_ratio, down_ratio = 구의 방정식을 이용해서 해당 좌표 평면 비스므리하게 없으면 오류.

    distance_ratio = 거리가 0.15m 이상 벌어지면 오류.
    '''
    def __init__(self, dir_path, over_ratio=1.25, down_ratio=0.75, distance_ratio=1.5):
        self.dir_path = dir_path
        self.over_ratio = over_ratio
        self.down_ratio = down_ratio
        self.distance_ratio = distance_ratio

        # self.point_labels = dict()

    # 데이터 복원 후 체크
    # @Data_Check
    # @Data_Double_Restoration
    @Data_Check
    @Data_Double_Restoration
    @Data_Check
    @Data_Restoration
    # 데이터 읽기
    async def read_data(self, file_path, over_ratio, down_ratio, distance_ratio):
        with open(file_path, 'rb') as hd:
            print(file_path)
            reader = c3d.Reader(hd)
            # 한 프레임마다
            # self.point_labels[file_path] = reader.point_labels
            data = [points for (i, points, analog) in reader.read_frames()]
            # 전체 데이터를 행렬로 바꿈
            data = np.array(data)
        return data

    @Data_Check
    @Data_Double_Restoration
    @Data_Check
    @Data_Restoration
    # 데이터 하나만 읽을 때. 파일 읽는게 아니라 데이터 하나만 넘겨줄때.
    # 프레임 하나의 데이터가 아니라 전체 프레임. 시작과 끝.
    async def data_restore(self, data, over_ratio, down_ratio, distance_ratio):
        return data
    # data_restore 실행하는 함수. ratio 문제가 있어서... decorator 말고 그냥 하는게 더 나아보이는데.
    async def weird_run(self, data):
        result_data = await self.data_restore(data, self.over_ratio, self.down_ratio, self.distance_ratio,)
        return result_data

    # 데이터 쓰기
    # c3d 파일로는 데이터를 저장 못할것 같고. db나 csv 파일에 따로 저장해야할 것 같음
    # analog 데이터를 수정 못함. 알 수가 없어
    async def write_c3d(self, data):
        # writer = c3d.Writer()
        # for _ in range(100):
        #     writer.add_frames(np.random.randn(30, 5))
            
        # with open('random-points.c3d', 'wb') as h:
        #     writer.write(h)
        pass
    # 실행
    async def run(self, write_file=False, ):
        
        if self.dir_path[-4] != '.':
            paths = (f'{path}/{filename}' for path, _, filenames in os.walk(self.dir_path) for filename in filenames)
            datas = [await self.read_data(path, self.over_ratio, self.down_ratio, self.distance_ratio,) for path in paths]

            for data, check_result in datas:
                # print(check_result)
                # print(data)
                # print(data.shape)
                await self.write_c3d(data)
        else:
            data, check_result = await self.read_data(self.dir_path, self.over_ratio, self.down_ratio, self.distance_ratio,)
            await self.write_c3d(data)

if __name__ == "__main__":

    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/'
    dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/'
    data_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/test/'
    
    a = Data_Read_Write(dir_path)

    # asyncio.run(a.run())

    b = Data_Test_Generate(data_path)
    test_data = b.run()
    result, point_labels =  asyncio.run(a.weird_run(test_data))
    print(result)