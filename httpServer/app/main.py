import socket

def main():
    print("Logs from your program will appear here! ")
    server_socket = socket.create_server(('localhost', 4221), reuse_port=True)
    with server_socket:
        server_socket.listen()
        conn, addr = server_socket.accept()  # Accept a connection
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

main()
