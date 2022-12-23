import socket
import select
import dataclasses

EOR = b'\r\n\r\n'
RESPONSE = """HTTP/1.1 200 OK
Server: blocking-python
Content-Length: 0

""".encode('utf-8')

# Initialize a non-blocking socket for our server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(1)
server_socket.setblocking(0)


@dataclasses.dataclass
class Connection:
    socket: socket.socket
    request: bytes = b''
    response: bytes = RESPONSE

connections = {}

with select.epoll() as epoll:
    # Register the server socket to our epoll object for incoming data (connections).
    epoll.register(server_socket.fileno(), select.EPOLLIN)
    while True:
        # Poll for events, waiting up to 1 second.
        events = epoll.poll(1)
        for fd, event in events:
            # Event on server socket means that there's a new incoming connection.
            if fd == server_socket.fileno():
                conn, address = server_socket.accept()
                conn.setblocking(0)
                # Register the incoming socket with epoll for incoming data (request data).
                epoll.register(conn.fileno(), select.EPOLLIN)
                connections[conn.fileno()] = Connection(socket=conn)
                continue

            conn = connections[fd]

            # Process pending read events.
            if event & select.EPOLLIN:
                conn.request += conn.socket.recv(1024)
                if EOR in conn.request:
                    # Set fd to be avaliable for write once the request is fully read.
                    epoll.modify(fd, select.EPOLLOUT)
                    print('-' * 40 + '\n' + conn.request.decode()[:-2])

            # Process pending write events
            elif event & select.EPOLLOUT:
                # Send response, subtract accepted bytes to the socket.
                byteswritten = conn.socket.send(conn.response)
                conn.responsep = conn.response[byteswritten:]
                # Unregister the connection socket from epoll if response is fully written.
                if len(conn.responsep) == 0:
                    epoll.modify(fd, 0)
                # Tell the other side that we're shutting it down.
                conn.socket.shutdown(socket.SHUT_RDWR)

            # Process hang up from client side
            elif event & select.EPOLLHUP:
                # Unregister the connection fd from epoll targets.
                epoll.unregister(fd)
                # Close the socket
                conn.socket.close()
                del connections[fd]
