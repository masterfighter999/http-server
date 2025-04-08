import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()  # wait for client
    data = connection.recv(1024)
    data_readable = data.decode().split("\r\n")
    response = b"HTTP/1.1 200 OK\r\n\r\n"
    if data_readable[0].split(" ")[1] != "/":
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    connection.sendall(response)

if __name__ == "__main__":
    main()
