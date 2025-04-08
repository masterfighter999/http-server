import socket  # noqa: F401

def main():
    print("Logs from your program will appear here!")
    try:
        server_socket = socket.create_server(("localhost", 4221), reuse_address=True)  # Use reuse_address
    except OSError as e:
        if "WinError 10048" in str(e):  # Check for address already in use error on Windows
            print("Error: Port 4221 is already in use. Please choose a different port.")
            return
        else:
            raise e

    server_socket.listen()
    print("Server is listening on port 4221...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")
        try:
            request_data = client_socket.recv(4096).decode()
            request_line = request_data.splitlines()[0]
            method, url_path, _ = request_line.split()  # Extract method and URL path

            if method == "GET":  # Handle only GET requests
                if url_path == "/":
                    status_code = "200 OK"
                    response_body = "Hello from the server!"

                elif url_path.startswith("/echo/"):
                    status_code = "200 OK"
                    response_body = url_path[6:] # Extract the string after /echo/
                else:
                    status_code = "404 Not Found"
                    response_body = "404 Not Found"
                    
                # Build the complete response with headers
                response = f"HTTP/1.1 {status_code}\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
                client_socket.sendall(response.encode())

            else: # Respond with Method Not Allowed for non-GET requests
                client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain\r\n\r\nMethod Not Allowed")


        except Exception as e:  # Generic exception handling
            print(f"Error processing request: {e}")
            client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request")
        finally:
            client_socket.close()


if __name__ == "__main__":
    main()
