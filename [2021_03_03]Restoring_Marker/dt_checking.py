import numpy as np
import os
from multiprocessing import Process, Manager, Lock
from collections import deque
from tqdm import tqdm
from operator import itemgetter

# 1. 소실된 점 복구.
class Data_Restoration:
    def run(self, data, no_data_point=None, ):
        
        result_data, no_data_point = self.data_restoration(data, no_data_point, )
        
        return result_data, no_data_point

    # 데이터 복구
    def data_restoration(self, data, no_data_point, ):
        # 원본 데이터에서 null 위치 체크
        if no_data_point is None:
            no_data_point =  self.__data_restoration_no_data_check__(data)
        # 데이터는 꽉 차있을 시.
        if no_data_point == list():
            return data, no_data_point

        datalists = self.__data_restoration_result__(no_data_point, data.shape[0])

        print('data fill full...')
        
        result_data =  self.__data_restoration_predict__(datalists, data)

        return result_data, no_data_point

    # 데이터에 null( 값이 들어 있지 않는 부분) 이 어디인지 체크
    def __data_restoration_no_data_check__(self, data):
        no_find = np.array([0., 0., 0., -1., -1.])
        check = np.where(data == no_find)

        no_data_point = set(zip(check[0], check[1])) #| set(zip(check2[0], check2[1]))
        no_data_point = list(no_data_point)
        return no_data_point

    # 전 값, 다음 값의 프레임, 마커 위치 datalists에 반환.
    def __data_restoration_result__(self, no_data_point, data_shape_first):
        
        # 이전 프레임의 정상 데이터 위치 값과 다음 프레임의 정상 데이터 위치값 찾기.
        no_data_point_np = np.array(no_data_point)
        no_data_point_minus = no_data_point_np - (1, 0)
        no_data_point_plus = no_data_point_np + (1, 0) # +1을하면 마지막 프레임에서 +1이 되므로 마지막 껀 오류가 발생
        # no data point 집합화
        no_data_point_minus = set([tuple(t) for t in no_data_point_minus])
        no_data_point_plus = set([tuple(t) for t in no_data_point_plus])
        no_data_point_set = set(no_data_point)

        # no data point와 겹치는 부분 빼기(차집합)
        before_frame_marker = no_data_point_minus - no_data_point_set
        after_frame_marker = no_data_point_plus - no_data_point_set

        before_frame_marker = sorted(before_frame_marker, key=itemgetter(1,0))
        after_frame_marker = sorted(after_frame_marker, key=itemgetter(1,0))
        
        before_frame_marker = np.array(before_frame_marker)
        after_frame_marker = np.array(after_frame_marker)
        # 아래 방법은 frame > marker가 되면 안되는 방법.
        # 마지막 프레임까지 정상적인 값이 없다면, 이전 프레임으로 채택한 데이터값을 다음 프레임값으로 채택하고, 
        # 이전 프레임의 그 전 프레임을 이전 프레임으로 재설정
        ### 여기에 오류가 있을 수 있겠네. 그 전 프레임이 비 정상적인 값이면 어떻게 해.
        over_frame = np.where(after_frame_marker == data_shape_first)
        after_frame_marker_modified = after_frame_marker.copy()
        after_frame_marker_modified[over_frame] = before_frame_marker[over_frame]
        before_frame_marker[over_frame] -= 1

        return zip(before_frame_marker, after_frame_marker, after_frame_marker_modified)

    # 예측값을 넣어서 result_data로 반환
    def __data_restoration_predict__(self, datalists, data):
        # datalists에 담겨져야 할 값 :
        # 정상적인 이전 데이터, 정상적인 다음 데이터의 좌표값. (before (frame, mark) after (frame, mark))
        # 이전 데이터와 다음 데이터의 프레임 차이. ( 좌표값만 알면 그냥 구할듯 ) after frame - before frame
        # 이전 데이터와 다음 데이터. (before data[frame][mark] after data[frame][mark])
        # for before frame
        for before_data, after_data, after_modified in tqdm(datalists):
            # time 은 frame 차이.
            # 보기 편하게
            (before_frame, before_mark) = before_data
            (after_frame, after_mark) = after_data
            (after_modified_frame, after_modified_mark) = after_modified

            time = after_frame - before_frame
            # after frame이 값을 넘어가는 경우 포함.
            predict_points = self.predict_before_after(data[before_frame, before_mark], data[after_modified_frame, after_modified_mark], time)
            # after_data frame 번호를 after_data frame 이 아니라 after_data 전 프레임으로 넣었으므로
            for i, frame in enumerate(range(before_frame+1, after_frame)):
                data[frame][after_mark] = predict_points[i]

        return data

    # 빈 값일 때
    # 이전 값과 다음 값으로 데이터 예측(평균값 사용)
    def predict_before_after(self, before_point, after_point, time):
        # 공차
        tolerance = (after_point - before_point) / (time)
        # before값에 등차 더한것 리스트. 등차수열.
        predict_point = [np.ravel(before_point + tolerance*i) for i in range(1, time)]
        
        predict_point = np.array(predict_point)
        
        return predict_point

    # 내적, 외적 사용
    def predict_before_after_vector(self, before_point, after_point, time):
        inner_product = np.dot(before_point, after_point) # 내적으로 사잇각 구하기
        outer_product = np.cross(before_point, after_point) # 외적으로 방향까지 구하기

        def mag(x):
            return np.sqrt(x.dot(x))
        # 외적은 +- 두개 나와야하는게 아닌가?

        # 각도 알고 시간 아니까 각속력만 구해서 변위값을 구하자.
        # time = 0.01sec

        # 각속도
        cos_theta = inner_product / (mag(before_point) * mag(after_point))
        # np.clip(cos_theta, -1, 1) # cos_theta 값을 -1~1사이의 값으로 전처리
        # sin_theta = np.sqrt(1 - cos_theta**2)
        theta = np.arccos(cos_theta)
        sin_theta = np.sin(theta)

        # 회전 변환
        rx = np.array([
            [1., 0., 0.],
            [0., cos_theta, -sin_theta],
            [0., sin_theta, cos_theta]
            ])
        ry = np.array([
            [cos_theta, 0., sin_theta],
            [0., 1., 0.],
            [-sin_theta, 0., cos_theta]
            ])
        rz = np.array([
            [cos_theta, -sin_theta, 0.],
            [sin_theta, cos_theta, 0.],
            [0., 0., 1.]
            ])

        angular_velocity = theta / time

        pass

# 2. 각 점들이 잘못되어있는지 확인
# 이전프레임에서 갑자기 너무 많이 움직이거나 방향이 변경됐는지 확인
# 값이 있는데 잘못된 값일 때
class Data_Check:
    def __init__(self, labels, up_down_ratio=np.array([1.,]), weight=0.3, distance_ratio=0.015, ):
        self.up_down_ratio=up_down_ratio
        self.weight=weight
        self.distance_ratio=distance_ratio
        self.labels = labels

    def run(self, data, no_data_point):

        data_restoration = Data_Restoration()
        
        distance_check_data = self.data_distance_check(data, self.distance_ratio)
        # sphere_check_data =  self.sphere_check(data, no_data_point, self.up_down_ratio, self.weight)
        # 이 시점에서 sphere_check_data와 data는 같은 주소값의 데이터 이므로, data를 넣어도 되지만,
        # 구별하기 위해서 sphere_check_data라는 변수 사용
        result_data, no_point_data = data_restoration.run(data, )

        return result_data, no_point_data

    # 데이터를 null값으로 처리.
    def data_change2zero(self, data, result_wrong_point):
        print('data change to null')
        # test = 0
        # for test, (frame, mark) in enumerate(result_wrong_point):
        #     data[frame][mark] = np.array([0., 0., 0., -1., -1.])
        # print(f'data check를 통해 {test}개의 오류 검출')
        print(f'data check를 통해 {len(result_wrong_point[0])}개의 오류 검출')
        data[result_wrong_point] = np.array([0., 0., 0., -1., -1.,])

    # 이건 문제점이 양 옆 두 구가 정상적이어야 사용 가능.
    # 2안 양 옆 두 구에서 평면 방정식을 이용해서 그 안에 값을 앞 뒤 등차수열 값으로.
    def sphere_check(self, data, no_data_point, up_down_ratio, weight,):
        # sphere left right point에 data, label 집어넣기.
        left_data, right_data, weird_data, left_sphere_radius, \
        right_sphere_radius, left_right_straight, frame_num = \
             self.__sphere_left_right_point__(data, self.labels)
        
        if len(left_data) == 0 :
            return data, no_data_point
        
        # 삼각함수 사용
        # 세변의 길이를 알기 때문에, 각을 구하고 평면 방정식의 원의 중심 좌표값과 반지름 값을 구함.
        # 좌구의 중심점(A)과 우구의 중심점(B)을 밑변으로 하고 좌구의 반지름과
        # 우구의 반지름을 각각 빗변으로 하는(두 빗변의 교차점 (C)) 삼각형의 각CAB 값.
        left_theta = np.arccos((left_right_straight**2 + left_sphere_radius**2 - right_sphere_radius**2) / (2*left_right_straight*left_sphere_radius))
        # 각 CBA 값
        right_theta = np.arccos((left_right_straight**2 + right_sphere_radius**2 - left_sphere_radius**2) / (2*left_right_straight*right_sphere_radius))
        # print(left_theta, right_theta)
        # print(np.argwhere(np.isnan(left_theta)))
        # 평면방정식에서 원의 반지름
        plane_radius = np.sin(left_theta) * left_sphere_radius
        # 좌측 삼각형 밑변
        base_left = np.arctan(left_theta) * plane_radius
        # 우측 삼각형 밑변
        base_right = np.arctan(right_theta) * plane_radius
        # 평면방정식에서 원의 중점
        plane_center = ( ((left_data.T * base_left) + (right_data.T * base_right)) / (base_left + base_right) ).T
        # weird_data와 평면 방정식에서 원의 중점과의 거리와 평면 방정식에서 원의 반지름 비율
        radius_ratio_for_weird_plane = self.calc_distance(weird_data, plane_center) / plane_radius
        # nan 위치(1, -1)을 벗어나면 정확한 값이 아니므로 weird_data라고 판명)
        where_nan = np.isnan(radius_ratio_for_weird_plane)
        # isnan은 true, false 반환, shape 변경.
        where_nan = np.reshape(where_nan, (frame_num, where_nan.shape[0]//frame_num , 1))
        # argwhere True 위치값 반환.
        where_nan = np.argwhere(where_nan)
        # print(len(where_nan))
        # where_nan 변수 집합화.
        where_nan = {(nan[0], nan[1]) for nan in where_nan}
        # where_nan = set(where_nan[:, :2])

        # radius_ratio_for_weird_plane가 1이 안되는 곳 검출
        radius_ratio_for_weird_plane = np.reshape(radius_ratio_for_weird_plane, (frame_num, radius_ratio_for_weird_plane.shape[0]//frame_num , 1))
        
        find_wrong_data_radius_ratio = np.where((up_down_ratio - weight >= radius_ratio_for_weird_plane) | (up_down_ratio + weight <= radius_ratio_for_weird_plane))
        find_wrong_data_radius_ratio_set = set(zip(find_wrong_data_radius_ratio[0], find_wrong_data_radius_ratio[1]))


        # numpy 일 경우에 이렇게 계산.
        # left_data**2 - right_data**2 -2( (left_data - right_data)*weird_data ) = left_sphere_radius**2 - right_sphere_radius**2

        # left_side = right_data*2 - left_data*2 - left_data*left_data + right_data*right_data. 두 항을 우변으로 옮김
        # left_side == 두 구의 방정식을 뺀 좌변
        # left_data나 right_data나 둘다 좌, 우 구의 중심 좌표.
        # (x-a)**2 + (y-b)**2 + (z-c)**2 =r**2
        # (x-d)**2 + (y-e)**2 + (z-f)**2 =r'**2
        
        # 평방
        # a**2 + b**2 + c**2 - d**2 - e**2 -f**2 - 2( (a-d)x + (b-e)y + (c-f)z ) = r**2 - r'**2
        # left_side = -2( (a-d)... (b-e)... (c-f)...)
        # left_side = 2*(right_data - left_data)
        left_side = -2*(left_data - right_data)
        # right_side == 두 구의 방정식을 뺀 우변

        right_side = left_sphere_radius*left_sphere_radius - right_sphere_radius*right_sphere_radius \
                    + np.sum(right_data*right_data - left_data*left_data, axis=1)
        
        # right_side = right_sphere_radius*right_sphere_radius - left_sphere_radius*left_sphere_radius \
        #             + np.sum(left_data*left_data - right_data*right_data, axis=1)

        # weird_data가 x, y, z이므로 직방과 평방을 연립하기 위해서는, 

        weird_result = np.sum(left_side * weird_data, axis=1)

        # 좌변과 우변의 값이 같아야 하니까. 같으면 ratio가 1이고 아니면 1초과 및 미만.
        ratio = weird_result/right_side
        ratio = np.reshape(ratio, (frame_num, ratio.shape[0]//frame_num , 1))
        
        # 새로 시도해본 방식
        # weight 값이 클수록 wrong data의 범위를 줄여줌. 그럼 오히려 값이 작을수록 더 많이 고치니 좋을 수도 있는데,
        # 오히려 더 고치는 것이 값의 정확도가 떨어짐.
        # 그렇지 않고 값을 변경하지 않는게 오히려 더 정확도가 올라가네. 소수점자리까지 체크해서 그런가봄
        weight = 0.3
        
        find_wrong_data = np.where((up_down_ratio - weight >= ratio) | (up_down_ratio + weight <= ratio))
        find_wrong_data = set(zip(find_wrong_data[0], find_wrong_data[1]))
        
        # wrong data라고 생각한 부분들 합집합 처리.
        # find_wrong_data = find_wrong_data #| where_nan #| find_wrong_data_radius_ratio_set
        find_wrong_data = where_nan
        # 전 프레임의 정상적인 데이터와 평면 방정식간의 가장 가까운 값을 데이터로 채워넣음.
        # - 정사영 내려서 나온 직선의 방정식
        # 이상한 데이터의 이전 프레임의 좌표에서 현재의 평면에 수선의 발을 내리고, 접하는 지점과 평면의 중심점을 잇는 직선 방정식을 통해,
        # 가장 가까운 위치 값을 알 수 있음.
        # x, y, z는 weird data
        # [find_wrong_data_radius_ratio] 현재 프레임의 원방, 점 P인 이전 프레임의 weird_data는 
        normal_vector = left_data / -2
        # 매개변수 k값
        # k = (right_side +\
        #     np.sum(-2*(normal_vector[find_wrong_data_radius_ratio]* weird_data[find_wrong_data_radius_ratio-1]), axis=1) ) /\
        #     np.sum(-2*(normal_vector[find_wrong_data_radius_ratio]**2) , axis=1)

        # k 구했으니, x, y ,z 값(평면 방정식에 수직인 벡터와 교점 좌표)을 구하고, 원의 중심과의 거리의 비율 r, a를 따져 내적을 구해 최단거리의 좌표값을 구함
        # 문제점 : 바로 전의 데이터가 정상적이어야 가능.


        # 거리가 벗어난 데이터를 null값으로 처리.
        self.data_change2zero(data, find_wrong_data)
        # test = 0
        # for frame, mark in find_wrong_data:
        #     test +=1
        #     data[frame][mark] = np.array([0., 0., 0., -1., -1.])
        # print(f'data check를 통해 {test}개의 오류 검출')
        
        return data

    def __sphere_left_right_point__(self, data, labels):
        # data, label 받아.
        label = [mark.rstrip() for mark in labels]
        weird_data_list = [
                            'LFHD', 'LBHD', 'RFHD', 'RBHD', 'C7',
                            'CLAV', 'RBAK','T10', 'STRN', 'RSHO',
                            'RUPA', 'RELB', 'RFRM', 'RWRB', 'RWRA',
                            'RFIN', 'RPSI', 'RASI', 'RTHI', 'RKNE',
                            'RTIB', 'RANK', 'RHEE',
                            'LSHO', 'LUPA', 'LELB', 'LFRM', 'LWRB',
                            'LWRA', 'LFIN', 'LPSI', 'LASI', 'LTHI',
                            'LKNE', 'LTIB', 'LANK', 'LHEE',
                            ]
        left_data_list = [
                            'RFHD', 'LFHD', 'LFHD', 'LBHD', 'LFHD',
                            'LSHO', 'T10', 'STRN', 'T10', 'CLAV',
                            'RSHO', 'RUPA', 'RELB', 'RFRM', 'RWRB',
                            'RWRA', 'LPSI', 'LASI', 'RASI', 'RTHI',
                            'RKNE', 'RTIB', 'RANK',
                            'CLAV', 'LSHO', 'LUPA', 'LELB', 'LFRM',
                            'LWRB', 'LWRA', 'RPSI', 'RASI', 'LASI',
                            'LTHI', 'LKNE', 'LTIB', 'LANK',
                            ]

        right_data_list = [
                            'C7', 'C7', 'C7', 'C7', 'RFHD',
                            'RSHO', 'CLAV', 'CLAV', 'CLAV', 'RUPA',
                            'RELB', 'RFRM', 'RWRB', 'RWRA', 'RFIN',
                            'RWRB', 'RASI', 'RPSI', 'RKNE', 'RTIB',
                            'RANK', 'RHEE', 'RTOE',
                            'LUPA', 'LELB', 'LFRM', 'LWRB', 'LWRA',
                            'LFIN', 'LWRB', 'LASI', 'LPSI', 'LKNE',
                            'LTIB', 'LANK', 'LHEE', 'LTOE',
                            ]

        label_mark_index = { label.index(weird) : {'left' : label.index(left), 'right' : label.index(right)} \
                            for weird, left, right in zip(weird_data_list, left_data_list, right_data_list)}

        mark_val = list(label_mark_index.values())
        frame_num = len(data)

        # 이전에 사용했던 방법
        # left_data = [data[frame][mark-1] for frame, mark in no_data_point if mark !=0 and mark != limit]
        # 여기를 조금 변경하자. 1차원 말고 2차원으로 만들면 절대 안돼. 프레임도 계산하게 되니까.
        left_data = [data[frame][mark['left']] for frame in range(frame_num) for mark in mark_val]
        right_data = [data[frame][mark['right']] for frame in range(frame_num) for mark in mark_val]
        weird_data = [data[frame][mark] for frame in range(frame_num) for mark in label_mark_index]

        left_data = np.array(left_data)
        right_data = np.array(right_data)
        weird_data = np.array(weird_data)

        # 첫 프레임의 데이터들을 사용하여 신체의 길이(반지름)을 구함. 첫 프레임의 데이터는 완전한 데이터라고 가정 했음.
        left_data_for_sphere_radius = np.array([data[0][mark['left']] for mark in mark_val])
        right_data_for_sphere_radius = np.array([data[0][mark['right']] for mark in mark_val])
        weird_data_for_sphere_radius = np.array([data[0][mark] for mark in label_mark_index])

        left_sphere_radius = self.calc_distance(left_data_for_sphere_radius, weird_data_for_sphere_radius)
        right_sphere_radius = self.calc_distance(right_data_for_sphere_radius, weird_data_for_sphere_radius)
        left_sphere_radius= np.append(left_sphere_radius, [left_sphere_radius for _ in range(frame_num-1)])
        right_sphere_radius= np.append(right_sphere_radius, [right_sphere_radius for _ in range(frame_num-1)])
        left_right_straight = self.calc_distance(left_data, right_data)

        return left_data, right_data, weird_data, left_sphere_radius, right_sphere_radius, left_right_straight, frame_num

    # 두 점 사이의 거리 계산.
    def calc_distance(self, before_point, present_point, axis=1):

        distance = before_point - present_point
        distance *= distance
        try:
            distance = np.sum(distance, axis=axis)
        except Exception as e:
            # 값을 하나씩 넣었을 때, 변경된 데이터 전송됐을 때.
            try:
                distance = np.sum(distance, axis=axis-1)
            except Exception as e:
                print(e)
        distance = np.sqrt(distance)
        return distance

    # 이전 프레임과의 거리 계산 후
    def data_distance_check(self, data, distance_ratio):
        # 이전 프레임과 현재 프레임
        before_data = data[:-1]
        present_data = data[1:]
        # 두 프레임간 거리 계산
        # axis는 숫자가 작을 수록 제일 바깥(리스트)부터라고 보면 됨 axis = 0 x축, axis = 1 y축, axis =2 z축.
        distance = self.calc_distance(before_data, present_data, axis=2)
        # distance의 shape를 3차원으로 다시 변경
        distance = np.reshape(distance, distance.shape+(1,))
        # distance의 맨 앞에 정상 데이터 한 줄 추가하여 find wrong data의 위치 값 을 data와 같도록 함.
        distance = np.insert(distance, 0, np.zeros_like(distance[0]), axis=0)

        # 잘못된 데이터의 위치값 찾음
        # distance_ratio = 0.015m
        find_wrong_data = np.where(distance > distance_ratio)
        # result_wrong_point = list(set(zip(find_wrong_data[0], find_wrong_data[1])))
        # 잘못된 데이터의 위치값에 있는 데이터를 0으로 변경
        # self.data_change2zero(data, (find_wrong_data[0], find_wrong_data[1]))
        self.data_change2zero(data, (find_wrong_data[0][:], find_wrong_data[1][:]))

        return data