import socket
import threading
import os
import sys

def main():
    # Ensure the directory for /files is passed or use default
    directory = sys.argv[2] if len(sys.argv) > 2 else "."

    def handle_req(client, addr):
        try:
            data = client.recv(1024).decode('utf-8', errors='replace')
            if not data:
                client.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                return

            req = data.split("\r\n")
            if len(req) < 1 or not req[0]:
                client.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                return

            try:
                method, path, _ = req[0].split(" ")
            except ValueError:
                client.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                return

            if method == "GET":
                if path == "/":
                    response = "HTTP/1.1 200 OK\r\n\r\n".encode()
                elif path.startswith("/echo/"):
                    echo_text = path[6:]
                    body = echo_text.encode()
                    response = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(body)}\r\n\r\n"
                    ).encode() + body
                elif path.startswith("/user-agent"):
                    user_agent = ""
                    for line in req:
                        if line.lower().startswith("user-agent:"):
                            user_agent = line.split(":", 1)[1].strip()
                            break
                    body = user_agent.encode()
                    response = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(body)}\r\n\r\n"
                    ).encode() + body
                elif path.startswith("/files/"):
                    filename = path[len("/files/"):]
                    file_path = os.path.join(directory, filename)
                    try:
                        with open(file_path, "rb") as f:
                            body = f.read()
                        response = (
                            f"HTTP/1.1 200 OK\r\n"
                            f"Content-Type: application/octet-stream\r\n"
                            f"Content-Length: {len(body)}\r\n\r\n"
                        ).encode() + body
                    except FileNotFoundError:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

            elif method == "POST" and path.startswith("/files/"):
                filename = path[len("/files/"):]
                file_path = os.path.join(directory, filename)

                content_length = 0
                for line in req:
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":")[1].strip())
                        break

                body = b""
                while len(body) < content_length:
                    body += client.recv(content_length - len(body))

                try:
                    with open(file_path, "wb") as f:
                        f.write(body)
                    response = "HTTP/1.1 201 Created\r\n\r\n".encode()
                except Exception as e:
                    print(f"Error writing file: {e}")
                    response = "HTTP/1.1 500 Internal Server Error\r\n\r\n".encode()

            else:
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode()

            client.send(response)

        except Exception as e:
            print(f"Error handling request from {addr}: {e}")
            client.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
        finally:
            client.close()

    server_socket = socket.create_server(("localhost", 4221))
    server_socket.listen()
    print("Server is listening on port 4221...")

    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_req, args=(client, addr)).start()

if __name__ == "__main__":
    main()
