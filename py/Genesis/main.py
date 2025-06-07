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

import socket
import selectors


def run_server(host: str = "127.0.0.1", port: int = 8080):
    S = selectors.DefaultSelector()

    def accept(socket: socket.socket):
        client_conn, client_address = socket.accept()
        print(f"> New connection from address: {client_address}")
        client_conn.setblocking(False)
        S.register(client_conn, selectors.EVENT_READ, read)

    def read(conn: socket.socket):
        try:
            data = conn.recv(1024)

            if data:
                print("> requesting")
                print(data.decode("utf-8"))

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type text/plain\r\n"
                    "Content-Length 20\r\n"
                    "\r\n"
                    "HELLO ON THIS SERVER"
                )

                conn.sendall(response.encode("utf-8"))
            S.unregister(conn)
            conn.close()

        except ConnectionResetError:
            S.unregister(conn)
            conn.close()

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    server_socket.setblocking(False)

    S.register(server_socket, selectors.EVENT_READ, accept)

    print(f"> serving on http://{host}:{port} ...")

    try:
        while True:
            events = S.select()
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)

    except KeyboardInterrupt:
        print("\n\r>> absolutely shutting down!")
    finally:
        server_socket.close()


if __name__ == "__main__":
    run_server()
