import socket

def main():
    print("Logs from your program will appear here! ")
    
    server_socket = socket.create_server(('localhost', 8000), reuse_port=True)
    server_socket.listen(5)  # Listen for incoming connections
    server_socket.accept()  

if __name__ == "__main__":
    main()
