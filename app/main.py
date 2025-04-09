import socket
import threading
import os
import sys

def main():
    def handle_req(client, addr):
        try:
            data = client.recv(1024).decode()
            req = data.split("\r\n")
            request_line = req[0].split(" ")
            method = request_line[0]  # Extract the HTTP method (GET or POST)
            path = request_line[1]   # Extract the path

            if method == "GET" and path == "/":
                # Handle root path
                response = "HTTP/1.1 200 OK\r\n\r\n".encode()
            elif method == "GET" and path.startswith("/echo"):
                # Handle echo endpoint
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
            elif method == "GET" and path.startswith("/user-agent"):
                # Handle user-agent endpoint
                user_agent = req[2].split(": ")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
            elif path.startswith("/files/"):
                # Extract the directory and filename
                directory = sys.argv[2]
                filename = path[len("/files/"):]  # Remove "/files/" from the path

                if method == "GET":
                    # Handle GET /files/{filename}
                    print(f"Requested file: {filename} in directory: {directory}")
                    try:
                        # Construct the full file path
                        file_path = os.path.join(directory, filename)
                        # Open the file in binary mode
                        with open(file_path, "rb") as f:
                            body = f.read()
                        # Create the HTTP response
                        response = (
                            f"HTTP/1.1 200 OK\r\n"
                            f"Content-Type: application/octet-stream\r\n"
                            f"Content-Length: {len(body)}\r\n\r\n"
                        ).encode() + body
                    except FileNotFoundError:
                        # File not found, return 404
                        response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
                    except Exception as e:
                        # Handle other exceptions
                        print(f"Error serving file: {e}")
                        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n".encode()

                elif method == "POST":
                    # Handle POST /files/{filename}
                    print(f"Creating file: {filename} in directory: {directory}")
                    try:
                        # Extract Content-Length header to determine the size of the body
                        content_length = 0
                        for header in req:
                            if header.startswith("Content-Length:"):
                                content_length = int(header.split(": ")[1])
                                break

                        # Read the request body
                        body = client.recv(content_length).decode()

                        # Construct the full file path
                        file_path = os.path.join(directory, filename)
                        # Write the body to the file
                        with open(file_path, "w") as f:
                            f.write(body)

                        # Return 201 Created response
                        response = "HTTP/1.1 201 Created\r\n\r\n".encode()
                    except Exception as e:
                        # Handle errors during file creation
                        print(f"Error creating file: {e}")
                        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n".encode()
                else:
                    # Unsupported method for /files/{filename}
                    response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode()
            else:
                # Handle unknown paths
                response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

            client.send(response)
        except Exception as e:
            print(f"Error handling request from {addr}: {e}")
        finally:
            client.close()

    # Create the server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    print("Server is listening on port 4221...")

    while True:
        client, addr = server_socket.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_req, args=(client, addr)).start()

if __name__ == "__main__":
    main()