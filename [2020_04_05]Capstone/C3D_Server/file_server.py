import socket
import capstone
import os

from multiprocessing import Process
from threading import Thread
import time

class Socket_Server:
    def __init__(self, path=None, host=socket.gethostname(), port = 9999, DATA_SEND = 2<<12):
        
        self.host = host
        self.port = port
        # 8096, 16192
        self.DATA_SEND = DATA_SEND
        self.path = path

    def run(self,):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(5)
            print('Socket is now Listening...')
            while True:
                client_socket, addr = s.accept()
                recv = Process(target=self.server, args=(client_socket, addr))
                recv.start(),recv.join()
        
    # 데이터 파일 받는 함수
    def server(self, c, addr):
        
        file_name = './my_workspace/datasets/before/2020/[2020_06_11]Socket_Data/C3D_Data_' \
                    + time.strftime('%Y-%m-%d-%Hh%Mm%Ss', time.localtime(time.time())) \
                    + '.c3d'
        # 파일 추가 저장. 덮어쓰기 x.
        # while True:
        #     if os.path.exists(file_name):
        #         file_name = file_name.replace('.c3d', '_modified.c3d')
        #     else:
        #         break
        # file_name = file_name.replace('.c3d', '_modified.c3d')
        
        with open(file_name, 'wb') as f :
            
            while True:
                # socket의 recv함수는 연결된 소켓으로부터 데이터를 받을 대기하는 함수입니다. 최초 4바이트를 대기합니다.

                # data = c.recv(4)
                # length = int.from_bytes(data, "little")
                # print('data length : ', length)

                # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.
                # C#의 BitConverter는 big엔디언으로 처리된다.
                print('Got connection from', addr)
                l = c.recv(self.DATA_SEND)
                print('Receiving...')
                while(l):
                    f.write(l)
                    l = c.recv(self.DATA_SEND)
                    print('Receiving...')
                    
                print('Done Receiving')
                break

        # 데이터 복원 후 저장
        print('Restoring...')
        try:
            data_read_write = capstone.Data_Read_Write(file_name)
            self.path = data_read_write.run(write_file=True)
            print('Done Restoring')
        except Exception as e:
            print(e)
            print('Restoring error...')
        
        # 저장된 csv 파일, 클라이언트 서버로 전송
        print('Sending...')

        # # 원본 파일 보내기
        # data, _, __ = data_read_write.read_data(self.path)

        # file_name = data_read_write.c3d2csv(data, self.path)

        # with open(file_name, 'rb') as f :
        #     length = os.stat(file_name).st_size
        #     print(length)
        #     # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
        #     c.sendall(length.to_bytes(4, byteorder='little'))

        #     # 데이터를 클라이언트로 전송한다.
        #     c.sendall(f.read())
        #     print('Send origin file')

        # 수정된 파일 보내기
        csv_path = self.path.replace('.c3d', '_modified.csv')
        csv_path = csv_path.replace('before', 'after')
        
        with open(csv_path, 'rb') as f :
            length = os.stat(csv_path).st_size
            print(length)
            # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
            # c.sendall(length.to_bytes(4, byteorder='little'))

            # 데이터를 클라이언트로 전송한다.
            c.sendall(f.read())
            print('Send modified file')
            # 파일 전송 끝난 걸 알림

        c.shutdown(1)
        # 파일 삭제

        print('Done Sending')

if __name__ == "__main__":
    
    server = Socket_Server()
    server.run()
