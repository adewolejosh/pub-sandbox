"""GENESIS [for a reason -> the beginning]"""
# Back to basics. I know. [who cares*]
# random notes. Yeah, I know
# Just tryna build a server from scratch
# ---
# using raw sockets, and then dived into using either
# context managers (using `with` in python -> which helps start and close the connection for us)
# or manually opening and closing the connection ourselves, using a while loop, while active we
# can receive requests and give some response.
# Though the former was short-lived, closes immediately after sending a response
# The other continues to handle the response.
# ---
# This made me play around into using TCP/UDP but below is just using the TCP (more reliable protocol) [old]
# as against the UDP (fire and forget guy) [old]
# Then finally trying to make sense, and remember the OSI model off-hand [old]
# Has 7 layers: (Application -> Presentation -> Session) -> Transport (TCP/UDP) -> Network (IP) -> Data Link -> Physical [old]
# pretty interesting. [old]
# ---
# switching into multi-client, event driven server
# we fired up multiple clients connected to the port using 'nc localhost 8080' and sent messages...
# also keyboard interrupt closed all open connections. GREAT!
# ---
# Now, a better approach is using selectors for select.
# To be fair, code seems nicer with selectors, though much more abstracted
# maybe explore how `selectors` work under the hood in python???
# just went to the library, it feels like a bunch of classes that listen to the fileobj you pass in
# and uses select to handle them gracefully. pretty cool stuff!
# ---
# moving on to asyncios :) pretty excited about this one
# a code-overhaul
# asyncio uses selector which uses select, all to start the server,
# using coroutines to manage several clients, but noticed it currently doesn't terminate
# unless we terminate all but on clients.
# ---
# we want to now broadcast the messages from clients back to all users
# as against one-to-one, let's go
# yeah, some success with that!
# also added alerting others when other addresses join in!

import asyncio
from typing import Any


connected_writers = set()


async def handle_client(reader: Any, writer: Any):
    addr = writer.get_extra_info("peername")
    print(f"> listening on this address: {addr}")
    connected_writers.add(writer)
    await broadcast(message=f"{writer} just joined")

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break

            message = data.decode().strip()
            print(f"> on {addr}, said...data: {message}")
            # response = f"You said: {message} \n"
            # writer.write(response.encode())
            # await writer.drain()
            broadcast_message = f"{addr} says: {message}"
            await broadcast(message=broadcast_message, exclude=writer)

    except ConnectionResetError:
        pass

    finally:
        connected_writers.remove(writer)
        print(f"> closed connection on address {addr}")
        writer.close()
        await writer.wait_closed()


async def broadcast(message: str, exclude=None):
    to_remove = set()
    for writer in connected_writers:
        if writer is exclude:
            continue

        try:
            writer.write(message.encode())
            await writer.drain()
        except (BrokenPipeError, ConnectionResetError):
            to_remove.add(writer)

    connected_writers.difference_update(to_remove)


async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8080)
    addr = server.sockets[0].getsockname()
    print(f":> started server with address: {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n\r> absolutely shutting down the server")
