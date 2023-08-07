import socket
import asyncio
import capstone
import os
class Socket_Server:
    def __init__(self, port=12345, DATA_SEND=2<<16, host=socket.gethostname()):
        self.port = port
        self.DATA_SEND = DATA_SEND
        self.host = host

    async def start_client(self, file_name):
        reader: asyncio.StreamReader
        writer: asyncio.StreamWriter

        reader, writer = await asyncio.open_connection(
                self.host,
                self.port,)
        print('[C]Connected')
        with open(file_name, 'rb') as f:
            writer.write(f.read())
        # writer.write(message.encode())
        await writer.drain()
        # print(f'[C]Send: {message!r}')

        data = await reader.read(self.DATA_SEND)
        # print(f'[C]Received: {data.decode()!r}')

        print('[C]Closing...')
        writer.close()
        await writer.wait_closed()


    async def handle_echo_tcp(
            self,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        print(addr)
        data = await reader.read(self.DATA_SEND)
        # message = data.decode()
        file_name = './my_workspace/datasets/before/[2020_06_11]Socket_Data/test.c3d'
        with open(file_name, 'wb') as f:
            f.write(data)
        # sock.getpeername()

        # print(f"[S]Received {message!r} from {addr!r}")
        # print(f'[S]Echoing: {message!r}')
        writer.write(data)
        await writer.drain()

        print("[S]Close the connection")
        writer.close()
        await writer.wait_closed()


    async def start_server(self,):
        server = await asyncio.start_server(
                self.handle_echo_tcp,
                self.host,
                self.port,
                limit=100000,)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()


    async def test(self, file_name):

        # 실행 후 꺼지지 않음
        # await asyncio.gather(
        #     self.start_server(),
        #     self.start_client(file_name)
        # )

        # 실행 후 timeout 후 꺼짐
        await asyncio.wait(
            [self.start_server(), self.start_client(file_name)], timeout=10.0
        )

if __name__ == "__main__":
    socket = Socket_Server()
    file_name = 'datasets/before/[2020_03_12]Auto_Marking/C3D_Edited/Case2_Edited.c3d'
    asyncio.run(socket.test(file_name), debug=True)
    