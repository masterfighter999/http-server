# Uncomment this to pass the first stage
import socket  # For creating server sockets
import threading  # For handling multiple client connections concurrently
import sys  # For accessing command-line arguments
import gzip  # For gzip compression

def main():
    # Function to handle individual client requests
    def handle_req(client, addr):
        try:
            # Receive data from the client (up to 1024 bytes)
            data = client.recv(1024).decode()
            # Split the received data into lines
            req = data.split('\r\n')
            # Extract the requested path from the first line of the request
            path = req[0].split(" ")[1]
            print(req)  # Log the request for debugging purposes

            # Handle GET requests
            if req[0].split(" ")[0] == "GET":
                if path == "/":
                    # Respond with a 200 OK for the root path
                    response = "HTTP/1.1 200 OK\r\n\r\n".encode()
                elif path.startswith('/echo'):
                    # Check if the "Accept-Encoding" header is present in the request
                    if req[2].startswith("Accept-Encoding"):
                        # Extract the encoding type from the "Accept-Encoding" header
                        encoding = req[2].split(": ")[1]
                        print(encoding)  # Log the encoding type for debugging purposes
                        if encoding == 'gzip':
                            # Respond with gzip-encoded content if the encoding is "gzip"
                            content = path[6:]
                            content = gzip.compress(content.encode())  # Gzip compress the content
                            print(content)  # Log the compressed content for debugging
                            response = f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n".encode() + content
                        elif ',' in encoding:
                            # Handle cases where multiple encodings are specified (e.g., "gzip, deflate")
                            encoding = [i.strip() for i in encoding.split(",")]  # Split and clean the encodings
                            if 'gzip' in encoding:
                                # Respond with gzip-encoded content if "gzip" is one of the encodings
                                content = path[6:]
                                content = gzip.compress(content.encode())
                                response = f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n".encode() + content
                            else:
                                # Respond with plain text if "gzip" is not in the list of encodings
                                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
                        else:
                            # Respond with plain text if the encoding is not "gzip"
                            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
                    else:
                        # Respond with plain text if the "Accept-Encoding" header is missing
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
                elif path.startswith("/user-agent"):
                    # Extract and respond with the User-Agent header
                    user_agent = req[2].split(": ")[1]
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
                elif path.startswith("/files"):
                    # Handle file retrieval requests
                    directory = sys.argv[2]  # Directory specified via command-line argument
                    filename = path[7:]  # Extract the filename from the path
                    print(directory, filename)  # Log the directory and filename
                    try:
                        # Open the requested file in read mode
                        with open(f"/{directory}/{filename}", "r") as f:
                            body = f.read()
                        # Respond with the file contents
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
                    except Exception as e:
                        # Respond with 404 Not Found if the file doesn't exist
                        response = f"HTTP/1.1 404 Not Found\r\n\r\n".encode()
                else:
                    # Respond with 404 Not Found for unknown paths
                    response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
                client.send(response)

            # Handle POST requests
            elif req[0].split(" ")[0] == "POST":
                if path.startswith("/files"):
                    # Handle file creation requests
                    directory = sys.argv[2]  # Directory specified via command-line argument
                    filename = path[7:]  # Extract the filename from the path
                    body = req[-1]  # Extract the request body
                    # Write the request body to the specified file
                    with open(f"/{directory}/{filename}", "w") as f:
                        f.write(body)
                    # Respond with 201 Created
                    response = "HTTP/1.1 201 Created\r\n\r\n".encode()
                client.send(response)
        except Exception as e:
            print(f"Error handling request from {addr}: {e}")
        finally:
            # Close the client connection
            client.close()

    # Create a server socket bound to localhost on port 4221
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is listening on port 4221...")

    # Continuously accept and handle client connections
    while True:
        client, addr = server_socket.accept()  # Accept a new client connection
        print(f"Connection from {addr}")
        # Handle the client in a new thread
        threading.Thread(target=handle_req, args=(client, addr)).start()
    

if __name__ == "__main__":
    main()