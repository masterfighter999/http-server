import socket  # Importing the socket module to handle network communication

def main():
    # Create a socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to localhost on port 4221
        s.bind(("localhost", 4221))
        # Start listening for incoming connections
        s.listen()
        # Accept a connection from a client
        conn, addr = s.accept()
        
        # Infinite loop to handle client requests
        while True:
            # Receive data from the client (up to 1024 bytes)
            data = conn.recv(1024)
            # Decode the received data and split it into request and headers
            request, headers = data.decode().split("\r\n", 1)
            # Extract the HTTP method and target (path) from the request line
            method, target = request.split(" ")[:2]
            
            # If no data is received, break the loop
            if not data:
                break
            
            # Handle requests based on the target path
            if target == "/":
                # Respond with a 200 OK status for the root path
                response = b"HTTP/1.1 200 OK\r\n\r\n"
            elif target.startswith("/echo/"):
                # Extract the value after "/echo/" and respond with it
                value = target.split("/echo/")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}".encode()
            else:
                # Respond with a 404 Not Found status for unknown paths
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            
            # Send the response back to the client
            conn.sendall(response)

if __name__ == "__main__":
    # Entry point of the program
    main()