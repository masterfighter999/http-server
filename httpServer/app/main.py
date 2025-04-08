import socket

def main():
    # You can use print statements as follows for debugging, they'll be visible in the logs.
    print("Logs from your program will appear here! ")
    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
 
    server_socket.accept()  # wait for client
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
 
    server_socket.accept()  # wait for client

if __name__ == "__main__":
    main()
