# restoring marker

## 2021 / 03 / 06

- 396 line : label_mark_index try except 해결 해야 함

## 2021 / 03 / 31

1. dt_checking.py file
* 249 line   

```python
    find_wrong_data = find_wrong_data | where_nan #| find_wrong_data_radius_ratio_set
```

* find_wrong_data 3개를 전부 다 한꺼번에 더하지 않고   
    find_wrong_data로 restore 한번,   
    where_nan으로 restore 한번,   
    find_wrong_data_radius_ratio_set으로 restore 한번,   
    과 같이 나누어서 restore하면 정확도가 괜찮아 지지 않을까?

* 258 line
```python
    k = (
        right_side +\
        np.sum(-2*(normal_vector[find_wrong_data_radius_ratio]* weird_data[find_wrong_data_radius_ratio-1]), axis=1) ) /\
        np.sum(-2*(normal_vector[find_wrong_data_radius_ratio]**2) , axis=1
        )
```

* k라는 매개변수 값 계산해야함. -> 구의 방정식을 사용하지 않는다면 계산하지 않아도 됨

* 매커니즘을 잘못 생각했음.
    + 1. 데이터 값이 0 있는지 확인 후 data restore
    + 2. data check
        - 거리 계산 후 0.15m 이상 벗어나면 data restore.
        - 구의 방정식을 통해 특정 좌표 내에 존재하는지 판단 후 없으면 data restore.
            - 구의 방정식은 채용하기 힘들 것 같음.
            - 이유 : 부정확한 마커의 양 옆 마커의 데이터 값이 정상적이라는 전제 하에 계산해야 함
                    그러나 양 옆의 좌표 값이 정상적인지는 확인을 못함.
                    또한 카메라로 데이터 측정 시, 팔의 길이는 고정값이 분명하지만,   
                    프레임 마다 팔의 길이가 조금이나마 다르게 측정될 수 있으므로,   
                    정상적인 프레임의 팔의 길이를 기준 삼아서 계산하면 오차가 발생할 수 밖에 없음.
                    마지막으로 데이터 파일마다 양 옆의 좌표 값을 하드코딩 해야함.

        - 단, data restore 방식은 이상 좌표값을 0으로 치환 후 1번 방식에서 사용한 data restore 방식을 그대로 사용.
        - data resotre 방식 : 현재 속력( 이상 좌표값 앞 뒤 프레임의 차)을 구한 후 이전 프레임에 속력을 더한 값을 채워넣음.

* 데이터 restore한 퍼센티지 계산할 때,
    소실 처리는 test data로 충분히 되지만, 변경 데이터는 측정하기 많이 힘듬(말 그대로 random 값으로 넣어야 하므로).   
    따라서, raw data file과 edited data file을 이용하여 변경 데이터 및 소실 데이터의 restore percentage를 계산해야 함.   
    raw data file을 restore 하여 edited data file과 비교 해야 함. -> compare_raw_edited.py   
    다만 문제점은 Stimulation, Start 마커가 없는 경우가 존재. 두가지 항목을 제외하고 비교.

## 2021 / 04 / 04

1. sample data download. -> can't use sphere check.

2. print percentage -> 지금 짜놓은 함수가 뭔가 이상한데... 고쳤는데 고친게 맞는지 알 수는 없잖아. 고치기 전과 고친 후의 test 에서만 확인 가능하고.   
이건 percentage of correction 클래스에서만 사용 가능한것이고, read and write 클래스에서는 이런식으로 하면 안됨.
 
3. sphere check 는 weird data의 양 옆 마커를 특정 지을 수 있을 경우에 사용.

4. dt_checking.py 148번째 줄 distance_check_data = self.data_distance_check(data, self.distance_ratio) 주석처리 해놓았음

## 2021 / 04 / 05
1. 해결 해야할 문제

    * c3d data 확인해보아야함 이미지로. -> Univ/4-1/Capstone/view_c3d_file.py로 확인해 본 결과, 평지 아래에 있음(z값이 -인듯)

    * data의 min max로 test data random 값 범위 설정.

    * distance로 restore시 변경값도 거의 대부분 복원 됨을 확인.

    * distance_ratio는 데이터마다 좌표 값의 크기가 다르기 때문에, 고정 값을 설정하기가 힘듬.   
        - 연구실에서 받은 파일은 0.15가 맞는듯.
        - c3d sample file은 좀 더 봐야 함.

    * sphere check가 지금 이상함. 수정해야함.

    * 20만건의 data change 발생 시, 속도가 느림.
        * 문제
            1. no_data_points를 튜플과 리스트로 묶긴 했지만, where에서 바로 나온 값을 data에 넣는것보다 훨씬 느림. (fill null)
            2. 최대 문제는 여기서 발생 : __data_restoration_result__함수에서 데이터 입력 과정이 오래 걸림.   
                이거 바꿔야 하는데 바꾸면 뒤엎어야함.
        * 해결방법
            1. where을 사용한 결과값을 data에서 참조하여 값 변경. ex) data[where_result] = np.array([...])
            2. 고민중... batch를 나눠서 thread 사용해보자 cpu더 쓰자. async는 되는건가?

    * c3d.py 파일 수정
        - 329 line : elems.frombytes(self.bytes) -> try except로 감쌈.
        - #886 line : if self.header.analog_count > 0: 조건문 부분 주석처리. -> 이걸 하면 restore 자체를 못함
        - 1071 line : add('RATE', 'analog samples per 3d frame', 4, '<f', analog.shape[1]) 부분 try except로 감쌈.

2. c3d sample file를 위한 distance 수정하기 -> present와 before의 데이터를 뺀 값의 min max에서 +- 시켜주자.
    * 이건 데이터가 정상적일때만 가능
    * tanh써봐...?
    * 자리수를 n이라 했을때, n*10^n 으로 나누고, 다음 tanh까지 (정규화)
    * 신경 써야 할 가중치 값 -> [1., 1., 1., 0., 0.] 에 곱할 percentage_ratio 값(중요도 낮음)과, distance 값(중요도 매우 높음). 0.115 정도에서 +- 0.015라는데, 문제는 100cm/s라서 1.0m/frame 해야하는데...
    * dt_checking.py의 __data_restoration_result__함수 수정할까말까... 수정 전에는 이론적으론 맞지만 속도가 느림. 쓰레드도 사용 못함. 수정 후 -> marker, frame 순으로 정렬한 후, frame 값에 -1, +1을 더함 -> -1 : [3,0 4,0 9,0 16,0] | +1 : [5,0 6,0 11,0 18,0] - origin frame, marker

## 2021 / 04 / 08

1. 해결해야할 것

    * dt_checking.py에서 Data_Restoration 클래스 안의 predict_before_after 함수와 __data_restoration_predict__함수에서   
    데이터에 하나씩 접근해서 값 수정하는것을 한꺼번에 수정할까 고민중. -> 한꺼번에 할 수는 있어도 고려해야할게 많음. 보류. (time변수와 같은 문제.)

    * data distance로 값 체크 시 -> 빈 데이터를 너무 많이 생성하므로, 제대로 값이 고쳐지지 않는것 같음.
    일단 ratio는 1.5나 8 사잇값으로 fix.
        1. 만약 한꺼번에 값을 수정한다면 -> no_data_point를 batchsize만큼 나누어서 restore. : 속도는 엄청 빠를듯.
        2. 하나씩 값을 수정한다면(마크 하나) -> 횟수가 일정 이상일때마다 restore. : 지금 굳이 고치지 않아도 됨.
        3. 이상하다? batch로 나누나 안나누나 결과는 같지 않나?

2. 끝난듯함

    * 여태 생성자에다가 값을 잘못 집어넣고 있었음. 이거 하나로 몇일동안 parameter에다가만 값 변동시키면서 정확도 측정도 못하고 가중치 값도 계산 못했어...   
    그래도 그 와중에 코드 수정해서 빅데이터도 빠른 시간 내에 수정할 수 있게 코드 고쳤음...   
    딱하나 아쉬운건 __data_restoration_predict__함수에서 값 수정하는 부분도 한꺼번에 수정할 수 있게 고치는건 아직 안한것.   
    -> before frame과 after frame 사이의 값들을 채워넣는 방법이 for문 말고 있나?

    * data check 부분을 한 번 더 실행시켜보자. -> 연속된 프레임의 값이 잘못되어있지만, 두 프레임간 거리가 가중치값 미만이라면 오류 표시를 안하므로.
    
    * 첫번째 데이터가 오류일 때, 0, 0, 0이 아닌 맨 처음 나오는 값을 첫번째 데이터와 맨 처음 나오는 frame까지 쭉 채움.
    * 첫번째 데이터가 0이 아니네. 그냥 하면 될듯

    * data check 부분에서 no_data_point가 0이 될 때까지 무한 루프를 통해 반복하는게 최종인가?

## 2021 / 04 / 08

1. 해결해야할 것

    * distance_ratio가 가장 중요한 가중치 값이므로, for문을 돌면서, 정확도가 가장 높은 값을 distance_ratio로? 아니면 이걸 경사하강법을 이용해서 정해봐?