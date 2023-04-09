from ezc3d import c3d
import numpy as np

if __name__=='__main__':
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/'
    dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw_real_copy/'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/'
    data_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/Case2_Edited.c3d'
    # data_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'
    # dir_path = 'my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case2_raw.c3d'
    path = 'C:/Users/Yun/Desktop/vscode_workspace/my_workspace/datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/Case1_Edited.c3d'
    c3d_to_compare = c3d(path)
    # Print the header
print("# ---- HEADER ---- #")
print(f"Number of points = {c3d_to_compare['header']['points']['size']}")
print(f"Point frame rate = {c3d_to_compare['header']['points']['frame_rate']}")
print(f"Index of the first point frame = {c3d_to_compare['header']['points']['first_frame']}")
print(f"Index of the last point frame = {c3d_to_compare['header']['points']['last_frame']}")
print("")
print(f"Number of analogs = {c3d_to_compare['header']['analogs']['size']}")
print(f"Analog frame rate = {c3d_to_compare['header']['analogs']['frame_rate']}")
print(f"Index of the first analog frame = {c3d_to_compare['header']['analogs']['first_frame']}")
print(f"Index of the last analog frame = {c3d_to_compare['header']['analogs']['last_frame']}")
print("")
print("")
# Print the parameters
print("# ---- PARAMETERS ---- #")
print(f"Number of points = {c3d_to_compare['parameters']['POINT']['USED']['value'][0]}")
print(f"Name of the points = {c3d_to_compare['parameters']['POINT']['LABELS']['value']}")
print(f"Point frame rate = {c3d_to_compare['parameters']['POINT']['RATE']['value'][0]}")
print(f"Number of frames = {c3d_to_compare['parameters']['POINT']['FRAMES']['value'][0]}")
# print(f"My point new Param = {c3d_to_compare['parameters']['POINT']['NEWPARAM']['value']}")
print("")
print(f"Number of analogs = {c3d_to_compare['parameters']['ANALOG']['USED']['value'][0]}")
print(f"Name of the analogs = {c3d_to_compare['parameters']['ANALOG']['LABELS']['value']}")
print(f"Analog frame rate = {c3d_to_compare['parameters']['ANALOG']['RATE']['value'][0]}")
print("")
# print(f"My NewGroup new Param = {c3d_to_compare['parameters']['NEWGROUP']['NEWPARAM']['value']}")
print("")
print("")
# Print the data
print("# ---- DATA ---- #")
# print(f" = {c3d_to_compare['data']['points'][0:3, :, :]}")
# print(f" = {c3d_to_compare['data']['analogs']}")
print(f" = {c3d_to_compare['data']['points'][0 : 3,: ,:]}")
print(f" = {len(c3d_to_compare['data']['points'][1][0])}")