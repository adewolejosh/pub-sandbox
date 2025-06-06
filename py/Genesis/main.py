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
# This made me play around into using TCP/UDP but below is just using the TCP (more reliable protocol)
# as against the UDP (fire and forget guy)
# Then finally trying to make sense, and remember the OSI model off-hand
# Has 7 layers: (Application -> Presentation -> Session) -> Transport (TCP/UDP) -> Network (IP) -> Data Link -> Physical
# pretty interesting.

import socket


def run_server(host: str = "127.0.0.1", port: int = 8080):
    socket_afn = socket.AF_INET
    socket_stream = socket.SOCK_STREAM

    with socket.socket(socket_afn, socket_stream) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((host, port))

        server_socket.listen(1)
        print(f"> serving on http://{host}:{port} ...")

        try:
            while True:
                client_connection, client_address = server_socket.accept()

                with client_connection:
                    request = client_connection.recv(1024).decode("utf-8")

                    print("here's the request")
                    print(request)

                    # prepare a response
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        "Content-Length: 13\r\n"
                        "\r\n"
                        "HELLO ON THIS SERVER"
                    )

                    client_connection.sendall(response.encode("utf-8"))
        except KeyboardInterrupt:
            client_connection.close()


if __name__ == "__main__":
    run_server()
