import socket

EOR = b'\r\n\r\n'
RESPONSE = """HTTP/1.1 200 OK
Server: blocking-python
Content-Length: 0

""".encode('utf-8')

# Initialize a blocking socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(1)

try:
    while True:
        # Wait for an incoming connection
        conn, _ = server_socket.accept()
        # Read the request into buffer fully
        request = b''
        while EOR not in request:
            request += conn.recv(1024)
        
        conn.send(RESPONSE)
        conn.close()
finally:
    server_socket.close()
