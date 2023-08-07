## file_client.py
import socket 

s = socket.socket()
# host = socket.gethostname()
host = 'su-surface'

DATA_SEND = 8096
port = 9999

s.connect((host, port))
# file_name = 'datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/Case2_Edited.c3d'
file_name = 'datasets/before/[2020_03_12]Auto_Marking/C3D_raw/Case1_raw.c3d'
with open(file_name, 'rb') as f:
    print('Sending...')
    l = f.read(DATA_SEND)
    while (l):
        print('Sending...')
        s.send(l)
        l = f.read(DATA_SEND)
    print('Done Sending')
    s.shutdown(socket.SHUT_WR)
    print(s.recv(DATA_SEND))
    s.close