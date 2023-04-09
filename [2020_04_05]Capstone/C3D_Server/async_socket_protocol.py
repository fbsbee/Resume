import asyncio


async def start_client(message: str):
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    reader, writer = await asyncio.open_connection(
            '127.0.0.1', 5577)
    print('[C]Connected')
    writer.write(message.encode())
    await writer.drain()
    print(f'[C]Send: {message!r}')

    data = await reader.read(100)
    print(f'[C]Received: {data.decode()!r}')

    print('[C]Closing...')
    writer.close()
    await writer.wait_closed()


async def handle_echo_tcp(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    print(addr)
    data = await reader.read(100)
    message = data.decode()
    # sock.getpeername()

    print(f"[S]Received {message!r} from {addr!r}")
    print(f'[S]Echoing: {message!r}')
    writer.write(data)
    await writer.drain()

    print("[S]Close the connection")
    writer.close()
    await writer.wait_closed()


async def start_server():
    server = await asyncio.start_server(
            handle_echo_tcp, '127.0.0.1',
            5577)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


async def test():
    words = "hello world apple banana shift orange pine"\
            .split()
    srv = asyncio.ensure_future(start_server())
    fs = [srv, *(asyncio.ensure_future(
        start_client(w)) for w in words[:])]
    await asyncio.wait(fs, timeout=4)


if __name__ == '__main__':
    asyncio.run(test(), debug=True)