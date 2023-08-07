import numpy as np
import c3d
import asyncio
import os

# 데이터 읽기
async def read_data(file_path, ):
    with open(file_path, 'rb') as hd:
        print(file_path)
        reader = c3d.Reader(hd)
        # 전체 데이터를 행렬로 바꿈
        label = reader.point_labels
        print(label)
        print(len(label))
        data = [points for (i, points, analog) in reader.read_frames()]
        data = np.array(data)
    return data

if __name__ == "__main__":
    dir_path = 'my_workspace/datasets/after/[2020_03_12]Auto_Marking'
    dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking'
    dir_path = 'my_workspace/datasets/before/[2020_06_11]Socket_Data'
    dir_path = 'my_workspace/datasets/after/[2020_06_11]Socket_Data'
    dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw_real_copy'
    paths = (f'{path}/{filename}' for path, _, filenames in os.walk(dir_path) for filename in filenames)
    for path in paths:
        try:
            data = asyncio.run(read_data(path))
            print(len(data[0]))

            # print(data)
            print('==========================================================')
        except Exception as e:
            print(e)
    