import socket
import threading

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    while True:
        client, addr = server_socket.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
    try:
        data = client.recv(1024).decode()
        req = data.split("\r\n")
        path = req[0].split(" ")[1]
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n".encode()
        elif path.startswith("/echo"):
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
        elif path.startswith("/user-agent"):
            user_agent = req[2].split(": ")[1]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        client.send(response)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()