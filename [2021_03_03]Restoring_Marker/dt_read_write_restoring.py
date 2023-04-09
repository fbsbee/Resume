import os
import c3d
import pandas as pd
import numpy as np
from collections import deque

from dt_checking import Data_Restoration, Data_Check
from dt_test import Data_Test_Generate

# 데이터 읽고 쓰기 복원까지. 메인 클래스.
class Data_Read_Write:
    '''
    percentage_ratio = 정확도를 측정하기 위한 비율로, 기본 값인 [1., 1., 1., 0., 0.] 에 곱할 값.

    up_down_ratio는 data check할 때 사용할 기본 값.

    weight는 percentage_ratio와 마찬가지로, data check 할 때 사용한 up_down_ratio에 곱할 값.

    over_ratio, down_ratio = 구의 방정식을 이용해서 해당 좌표 평면 비스므리하게 없으면 오류.

    distance_ratio = 거리가 0.15m 이상 벌어지면 오류.

    폴더를 읽을 때에는 맨 끝에 "/"를 항상 붙여줘야 함.
    '''
    def __init__(self, dir_path, up_down_ratio=np.array([1.,]), weight=0.3, distance_ratio=0.15, percentage_ratio=0.95, ):
        self.dir_path = dir_path
        self.up_down_ratio = up_down_ratio
        self.weight = weight
        self.distance_ratio = distance_ratio
        self.percentage_ratio = percentage_ratio
        # self.point_labels = dict()
        
    # 데이터 읽기
    def read_data(self, file_path, ):
        
        with open(file_path, 'rb') as hd:
            reader = c3d.Reader(hd)
            # 한 프레임마다
            # self.point_labels[file_path] = reader.point_labels

            labels = reader.point_labels
            
            # 전체 데이터를 행렬로 바꿈
            origin_data = [(i, points, analog) for (i, points, analog) in reader.read_frames()]
            # print(origin_data)
            data = [points for (i, points, analog) in origin_data]
            analog_data = [analog for (i, points, analog) in origin_data]

            # data = [points for (i, points, analog) in reader.read_frames()]
            
            analog_data = np.array(analog_data)
            data = np.array(data)

        return data, analog_data, labels

    # 데이터 쓰기
    # c3d 파일로는 데이터를 저장 못할것 같고. db나 csv 파일에 따로 저장해야할 것 같음
    def write_c3d(self, data, analog_data, file_path, rename='_modified'):
        # 파일 이름 적는 곳
        dir_name = file_path[:file_path.rfind('/')]
        file_path = file_path[file_path.rfind('/'):]

        dir_name = dir_name.replace('before', 'after')
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_path = file_path.replace('.c3d', f'{rename}.c3d')
        file_path = dir_name + file_path

        # 파일 쓰기
        print('wrting file...')
        writer = c3d.Writer()
        for i in range(data.shape[0]):
            # writer.add_frames([(data[i, :], np.array([[]]))])
            writer.add_frames([(-data[i, :], analog_data[i, :])])
        
        with open(file_path, 'wb') as h:
            writer.write(h)

        # c3d 파일 csv로 변환
        self.c3d2csv(data, file_path)

        print(f'write file at : {file_path}')
        print('********************************************************************************************************')

        return file_path

    # c3d 파일 csv 파일로 변환. analog 데이터는 변환하지 않았음.
    def c3d2csv(self, data, file_name):
        # 파일 이름 csv로 변환
        file_name = file_name.replace('.c3d', '.csv')
        data = data.copy()
        # 데이터가 x, y, z 순으로 들어있지 않고 x, z, y 순으로 들어있어서 이렇게 적었음.
        # 올바르게 들어가 있다면, x, y, z 순서대로 넣으면 됨.
        data = np.array([[[x, z, y] for x, y, z, err, cam in frame_data] for frame_data in data])
        # data = np.array([[[x, y, z] for x, y, z, err, cam in frame_data] for frame_data in data])
        # data = np.array([[[y, z, x] for x, y, z, err, cam in frame_data] for frame_data in data])
        # 데이터 모양 구하기
        frame, mark, point = data.shape
        # 데이터 형식 변환
        data = data.reshape((frame, mark*point))
        # 데이터 프레임 생성
        csv_data = pd.DataFrame(data)
        # csv로 저장, header = column 쓰냐 안쓰냐.
        csv_data.to_csv(file_name, sep=',', mode='w', header=False)
        
    # 실행
    def run(self, write_file=False):
        # 파일이 아니면 == 폴더 이면.
        if self.dir_path[-4] != '.':
            paths = (f'{path}/{filename}' for path, _, filenames in os.walk(self.dir_path) for filename in filenames)
            datas = (( self.read_data(path, ), path) for path in paths)
            for (data, analog_data, labels), file_path in datas:
                print(file_path)
                result, no_data_point = self.data_restore(data.copy(), labels)
                self.print_percentage(no_data_point, percentage_ratio=self.percentage_ratio)

                if write_file:
                    # self.write_c3d(result, analog_data, file_path)
                    self.write_c3d(result, analog_data, file_path)
        # 파일이면
        else:
            print(self.dir_path)
            data, analog_data, labels = self.read_data(self.dir_path, )
            result, no_data_point = self.data_restore(data.copy(), labels)
            self.print_percentage(no_data_point, percentage_ratio=self.percentage_ratio)

            if write_file:
                self.write_c3d(result, analog_data, self.dir_path)
        return result

    def data_restore(self, data, labels):
        # 데이터 복원
        data_restoration = Data_Restoration()
        # before_no_data_point=고치기 전 이상한 곳 갯수
        data_restore, before_no_data_point =  data_restoration.run(data, )

        # 데이터 검수 및 복원
        data_check = Data_Check(labels, up_down_ratio=self.up_down_ratio, weight=self.weight, distance_ratio=self.distance_ratio, )
        # before_no_data_point=값이 이상한 곳. 못고친 곳. 얘를어쩌지? 이건 다시 수정해도 그대로야.
        # 한번 더 실행
        # 연속된 프레임의 값이 잘못되어있지만, 두 프레임간 거리가 가중치값 미만이라면 오류 표시를 안하므로
        no_data_point_list = deque()
        while True:
            data_restore, before_no_data_point_check = data_check.run(data_restore, before_no_data_point)
            if before_no_data_point_check == list():
                break
            no_data_point_list.append(before_no_data_point_check)
        print(f'data check count : {len(no_data_point_list)}')
        try:
            before_no_data_point = list(map(set, no_data_point_list))[0]
        except:
            before_no_data_point = None
        
        return data_restore, before_no_data_point

    def print_percentage(self, before_no_data_point, data=None, data_restore=None, percentage_ratio=0.05):
        try:
            before_weird = len(before_no_data_point)
        except:
            before_weird = before_no_data_point
        print(f'before the number of weird data = {before_weird}')
        if data is not None:
            ## 고친 후 이상한 곳 갯수. 2번째 방법
            # find == 값이 벗어나서 제대로 고쳐지지 않은 값.
            # find 조건은 원본과의 비율이 95퍼센트 밑인 경우 정확하지 않다고 판단.
            check = data / data_restore
            find = np.where((check > 1+percentage_ratio) | (check < 1-percentage_ratio))

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

# 정확도 측정
class Percentage_of_Correction:
    '''
    err_percentage = 데이터가 수정된 정도. but random으로 데이터를 수정하므로, 20% 수정시 err_percentage = 0.222와 가깝게, 40% 수정시 0.505, 60% 수정시 0.9에 가깝게.
    pattern =  0 : 소실 + 변경, 1 : 소실, 2: 변경
    percentage_ratio = 5% 내외만 정확하다고 판단.
    distance_ratio = 
    '''
    def __init__(self, path, err_percentage=0.9, pattern=1, percentage_ratio=0.05, distance_ratio=0.15, ):
        self.path = path
        self.err_percentage = err_percentage
        self.pattern = pattern
        self.percentage_ratio = percentage_ratio
        self.distance_ratio = distance_ratio
        # self.read_write = Data_Read_Write(dir_path=self.path, distance_ratio=self.distance_ratio, )

    def run(self, write_file=False):

        self.read_write = Data_Read_Write(dir_path=self.path, distance_ratio=self.distance_ratio, )

        if self.path[-4] != '.':
            paths = [f'{path}/{filename}' for path, _, filenames in os.walk(self.path) for filename in filenames]
            datas = (( self.read_write.read_data(path, ), path) for path in paths)
            test_generate = ( Data_Test_Generate(path, self.err_percentage) for path in paths)
            for (origin_data, analog_data, labels), file_path in datas:
                print(file_path)
                test_data, modified_data_num = next(test_generate).run(pattern=self.pattern)
                restore_data, no_data_point = self.read_write.data_restore(test_data.copy(), labels)

                self.read_write.print_percentage(before_no_data_point=modified_data_num, data=origin_data, data_restore=restore_data, percentage_ratio=self.percentage_ratio)
                if write_file:
                    # 원본
                    self.read_write.write_c3d(origin_data, analog_data, file_path, rename='_original')
                    # 테스트 데이터
                    self.read_write.write_c3d(test_data, analog_data, file_path, rename='_test')
                    # 복원 데이터
                    self.read_write.write_c3d(restore_data, analog_data, file_path, rename='_restore')
        # 파일이면
        else:
            # 데이터 읽음
            # read_write = Data_Read_Write(self.path)
            # data_check = Data_Check(labels=read_write.labels)
            test_generate = Data_Test_Generate(self.path, self.err_percentage)
            # 실제 데이터A
            origin_data, analog_data, labels = self.read_write.read_data(self.path)
            # 테스트 데이터 생성
            # 0은 혼합, 1은 소실만, 2는 위치 변경만
            test_data, modified_data_num = test_generate.run(pattern=self.pattern)

            # self.data_distance_check(origin_data, self.distance_ratio)
            # self.data_distance_check(test_data, self.distance_ratio)
            # a number of 복수 = 복수, the number of 복수 = 단수
            #restore_data를 test_data로 변경
            restore_data, no_data_point = self.read_write.data_restore(test_data.copy(), labels)
            self.read_write.print_percentage(before_no_data_point=modified_data_num, data=origin_data, data_restore=restore_data, percentage_ratio=self.percentage_ratio)

            if write_file:
                # self.write_c3d(origin_data)
                # 원본
                self.read_write.write_c3d(origin_data, analog_data, self.path, rename='_original')
                # 테스트 데이터
                self.read_write.write_c3d(test_data, analog_data, self.path, rename='_test')
                # 복원 데이터
                self.read_write.write_c3d(restore_data, analog_data, self.path, rename='_restore')
            # 데이터 이상한곳 출력해보기
            # for frame, mark in weird_data_point:
            #     print(f'here : {check[frame][mark]}')
        # return restore_data, origin_data, test_data
        
if __name__ == "__main__":
    # dir_path = 'datasets/before/[2020_03_12]Auto_Marking/C3D_raw/'
    dir_path = 'datasets/before/2020/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'datasets/after/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/'
    # data_path = 'datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'
    # dir_path = 'datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'

    # dir_path = 'datasets/before/[2020_03_12]Auto_Marking/Sample00_test/'
    # dir_path = 'datasets/before/[2020_03_12]Auto_Marking/demo/'
    # dir_path = 'datasets/after/[2020_03_12]Auto_Marking/'
    asdf = 'datasets/before/2020/[2020_03_12]Auto_Marking/Sample00_test/Motion Analysis Corporation/Walk1.c3d'
    raw_path = 'datasets/before/2020/[2020_03_12]Auto_Marking/C3D_raw/Case1_raw.c3d'
    # test_data_path = 'datasets/after/[2020_06_11]Socket_Data/'
    # read_write = Data_Read_Write(asdf, )
    write_file = True
    write_file = False

    raw_path = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    data_path = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_Edited/Case1_Edited.c3d'
    data_path2 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample29-first/OptiTrack-IITSEC2007.c3d'
    data_path3 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample31-second/large01.c3d'
    data_path4 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample31-second/large02.c3d'
    data_path5 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample29-first/OptiTrack-IITSEC2007_modified.c3d'
    data_path6 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample00_test/Innovative Sports Training/Static Pose.c3d' # (120, 30, 5)
    dir_path = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/C3D_Edited/'
    dir_path1 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample29-first/' # (7931, 34, 5) (3000, 38, 5)
    dir_path2 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample31-second/' # (72610, 52, 5) (73285, 42, 5)
    dir_path3 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample17/' # (4038, 10, 5)
    dir_path4 = '../../../OneDrive - 청주대학교/datasets/before/2020/[2020_03_12]Auto_Marking/Sample00_test/'
    # dir_path3 = 'datasets/before/2020/[2020_03_12]Auto_Marking/program_sample'
    # percentage_ratio = 정확도를 측정하기 위한 기준(weight) 비율로, 기본 값인 [1., 1., 1., 0., 0.] 에 곱할 값.
    # read_write = Data_Read_Write(dir_path, percentage_ratio=0.95 )
    # read_write = Data_Read_Write(dir_path1, percentage_ratio=0.95, distance_ratio=100 )
    # restore_data = read_write.run(write_file=write_file)
    # pattern 0 : 소실 + 변경, 1 : 소실, 2: 변경
    # percentage = Percentage_of_Correction(dir_path, err_percentage=0.222, pattern=0, percentage_ratio=0.95, distance_ratio=0.15, ) # 기존 data file
    percentage = Percentage_of_Correction(dir_path1, err_percentage=0.9, pattern=0, percentage_ratio=0.05, distance_ratio=100, ) # facial-3716개, opti-805개 정도가 원래 이상하다고 측정이 됨 #0.222, 0.505, 0.9 
    # percentage = Percentage_of_Correction(dir_path2, err_percentage=0.222, pattern=0, percentage_ratio=0.95, distance_ratio=50, )
    # percentage = Percentage_of_Correction(data_path6, err_percentage=0.9, pattern=0, percentage_ratio=0.95, distance_ratio=0.15, )
    percentage.run(write_file)
    # percentage.file_compare(dir_path, edited_path)