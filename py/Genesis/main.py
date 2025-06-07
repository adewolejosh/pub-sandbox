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
# ---
# two more things to do: parsing HTTP requests and gracefully shutting down
# ---
# parsing? some overhaul
# http-parsing from scratch, handling requests, 404, pinging and all that
# Let's goooooo!
# ---

import socket


def parsed_response(request: str):
    lines = request.split("\r\n")
    request_line = lines[0]
    method, path, version = request_line.split()

    headers = {}
    for line in lines[1:]:
        if line == "":
            break

        k, v = line.split(":", 1)
        headers[k.strip()] = v.strip()

    allowed_paths = ["/hello", "/ping"]
    print(f"heressss path {path}")
    if path not in allowed_paths:
        return {
            "method": method,
            "path": path,
            "version": version,
            "headers": headers,
            "code": 404,
        }

    if "ping" in path:
        return {
            "method": method,
            "path": path + "-pong",
            "version": version,
            "headers": headers,
            "code": 200,
        }

    return {
        "method": method,
        "path": path,
        "version": version,
        "headers": headers,
        "code": 200,
    }


def run_server(host: str = "127.0.0.1", port: int = 8080):
    socket_afn = socket.AF_INET
    socket_stream = socket.SOCK_STREAM

    with socket.socket(socket_afn, socket_stream) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"> listening on {host}:{port}")

        while True:
            client_conn, client_addr = server_socket.accept()

            with client_conn as conn:
                data = conn.recv(1024).decode("utf-8")

                print("Data gotten from request")
                print(data)

                parsed_res = parsed_response(data)

                print("ALL WE ARE SAYING, HAHA")
                print(parsed_res)

                res_body = f"Finally! {parsed_res['path']}"
                response = (
                    f"HTTP/1.1 {parsed_res['code']} OK\r\n"
                    "Content-Type: text/plain\r\n"
                    f"Content-Length: {len(res_body)}\r\n"
                    "\r\n"
                    f"{res_body}"
                )
                conn.sendall(response.encode())


if __name__ == "__main__":
    try:
        run_server()

    except KeyboardInterrupt:
        print("\n\r> absolutely shutting down the server")
