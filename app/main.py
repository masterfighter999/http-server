import socket
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 4221))
        s.listen()
        conn, addr = s.accept()
        while True:
            data = conn.recv(1024)
            request, headers = data.decode().split("\r\n", 1)
            method, target = request.split(" ")[:2]
            if not data:
                break
            if target == "/":
                response = b"HTTP/1.1 200 OK\r\n\r\n"
            elif target.startswith("/echo/"):
                value = target.split("/echo/")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}".encode()
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            conn.sendall(response)
if __name__ == "__main__":
    main()