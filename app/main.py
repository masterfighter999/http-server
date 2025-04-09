import socket  # Import the socket module for network communication
import threading  # Import the threading module to handle multiple clients concurrently
import os  # Import the os module for file path operations
import sys  # Import the sys module to access command-line arguments

def main():
    """
    Main function to create and run the HTTP server.
    """
    def handle_req(client, addr):
        """
        Handles a single client request.

        Args:
            client: The client socket.
            addr: The client's address.
        """
        try:
            # Receive data from the client (up to 1024 bytes) and decode it to a string
            data = client.recv(1024).decode()
            # Split the received data into lines based on CRLF
            req = data.split("\r\n")
            # Parse the request line to extract the HTTP method and path
            method, path, _ = req[0].split(" ")

            # Handle GET requests
            if method == "GET":
                if path == "/":
                    # Respond with 200 OK for the root path
                    response = "HTTP/1.1 200 OK\r\n\r\n".encode()
                elif path.startswith("/echo"):
                    # Respond with 200 OK and echo the path for /echo endpoint
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
                elif path.startswith("/user-agent"):
                    # Respond with 200 OK and the user-agent for /user-agent endpoint
                    user_agent = req[2].split(": ")[1]
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
                elif path.startswith("/files/"):
                    # Serve files from the specified directory
                    directory = sys.argv[2] 
                    filename = path[len("/files/"):]
                    file_path = os.path.join(directory, filename)
                    try:
                        # Open the file in binary read mode
                        with open(file_path, "rb") as f:
                            body = f.read()
                        # Construct the 200 OK response with file content
                        response = (
                            f"HTTP/1.1 200 OK\r\n"
                            f"Content-Type: application/octet-stream\r\n"
                            f"Content-Length: {len(body)}\r\n\r\n"
                        ).encode() + body
                    except FileNotFoundError:
                        # Respond with 404 Not Found if file not found
                        response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
                    except Exception as e:
                        # Respond with 500 Internal Server Error for other exceptions
                        print(f"Error serving file: {e}")
                        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n".encode()
                else:
                    # Respond with 404 Not Found for unknown paths
                    response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

            # Handle POST requests to create files
            elif method == "POST" and path.startswith("/files/"):
                directory = sys.argv[2]  # Get the directory from command-line arguments
                filename = path[len("/files/"):]  # Extract the filename from the path
                file_path = os.path.join(directory, filename)

                # Find the Content-Length header
                content_length = 0
                for line in req:
                    if line.startswith('Content-Length:'):
                        content_length = int(line.split(':')[1].strip())
                        break

                # Receive the request body
                body = client.recv(content_length)  # Receive as bytes
                
                try:
                    # Open the file in binary write mode and write the received body to it
                    with open(file_path, "wb") as f:
                        f.write(body)
                    # Respond with 201 Created indicating the file was successfully created
                    response = "HTTP/1.1 201 Created\r\n\r\n".encode()
                except Exception as e:
                    # Respond with 500 Internal Server Error if file creation fails
                    print(f"Error creating file: {e}")
                    response = "HTTP/1.1 500 Internal Server Error\r\n\r\n".encode()

            else:
                # Respond with 405 Method Not Allowed for unsupported methods
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode()

            # Send the response to the client
            client.send(response)
        except Exception as e:
            print(f"Error handling request from {addr}: {e}")
        finally:
            # Close the client socket
            client.close()

    # Create the server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    # Start listening for incoming connections
    server_socket.listen()
    print("Server is listening on port 4221...")

    while True:
        # Accept a client connection
        client, addr = server_socket.accept()
        print(f"Connection from {addr}")
        # Handle the client request in a separate thread
        threading.Thread(target=handle_req, args=(client, addr)).start()

# Entry point for the script
if __name__ == "__main__":
    main()
