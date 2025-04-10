# Uncomment this to pass the first stage
import socket
import threading
import sys
import gzip

def main():
    def handle_req(client, addr):
        data = client.recv(1024).decode()
        req = data.split('\r\n')
        path = req[0].split(" ")[1]
        print(req)
        if req[0].split(" ")[0] == "GET":
            if path == "/":
                response = "HTTP/1.1 200 OK\r\n\r\n".encode()  
            elif path.startswith('/echo'):
                if req[2].startswith("Accept-Encoding"):
                    encoding = req[2].split(": ")[1]
                    print(encoding)
                    if encoding == 'gzip':
                        content = path[6:]
                        #Gzip compress the content
                        content = gzip.compress(content.encode())
                        print(content)
                        response = f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n".encode()+content
                    elif ',' in encoding:
                        encoding = [i.strip() for i in encoding.split(",")]
                        if 'gzip' in encoding:
                            content = path[6:]
                            content = gzip.compress(content.encode())
                            response = f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n{content}".encode()
                        else:
                            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
                    else:
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
                else:
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
            elif path.startswith("/user-agent"):
                user_agent = req[2].split(": ")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
            elif path.startswith("/files"):
                directory = sys.argv[2]
                filename = path[7:]
                print(directory, filename)
                try:
                    with open(f"/{directory}/{filename}", "r") as f:
                        body = f.read()
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
                except Exception as e:
                    response = f"HTTP/1.1 404 Not Found\r\n\r\n".encode()
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
            client.send(response)

        elif req[0].split(" ")[0] == "POST":
            if path.startswith("/files"):
                directory = sys.argv[2]
                filename = path[7:]
                body = req[-1]
                with open(f"/{directory}/{filename}", "w") as f:
                    f.write(body)
                response = "HTTP/1.1 201 Created\r\n\r\n".encode()
            client.send(response)
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:    
        client, addr = server_socket.accept()
        threading.Thread(target=handle_req, args=(client, addr)).start()
    

if __name__ == "__main__":
    main()