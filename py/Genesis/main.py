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

import socket
import select


def run_server(host: str = "127.0.0.1", port: int = 8080):
    socket_afn = socket.AF_INET
    socket_stream = socket.SOCK_STREAM

    # with socket.socket(socket_afn, socket_stream) as server_socket:
    server_socket = socket.socket(socket_afn, socket_stream)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"> serving on http://{host}:{port} ...")

    # we can non-block here right???
    server_socket.setblocking(False)

    sockets = [server_socket]
    try:
        while True:
            readable, _, _ = select.select(sockets, [], [])

            for sock in readable:
                if sock is server_socket:
                    client_sock, client_add = server_socket.accept()
                    print(
                        f"> 'we got a match' :) hahha, lol. New Connection from: {client_add}"
                    )
                    client_sock.setblocking(False)
                    sockets.append(client_sock)
                else:
                    try:
                        request = sock.recv(1024)
                        if request:
                            print("> receiving???")
                            print(request.decode("utf-8"))

                            response = (
                                "HTTP/1.1 200 OK\r\n"
                                "Content-Type text/plain\r\n"
                                "Content-Length 20\r\n"
                                "\r\n"
                                "HELLO ON THIS SERVER"
                            )

                            sock.sendall(response.encode("utf-8"))
                            sockets.remove(sock)
                            sock.close()

                        else:
                            sockets.remove(sock)
                            sock.close()

                    except ConnectionRefusedError:
                        sockets.remove(sock)
                        sock.close()

    except KeyboardInterrupt:
        print("\n\r>> absolutely shutting down!")
        for sock in sockets:
            sock.close()


if __name__ == "__main__":
    run_server()
