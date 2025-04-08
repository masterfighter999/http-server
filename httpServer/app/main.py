import socket

def main():
    # You can use print statements as follows for debugging, they'll be visible in the logs.
    print("Logs from your program will appear here! ")
    # Uncomment this to pass the first stage
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 4221))
    server_socket.listen()  # wait for client
 

if __name__ == "__main__":
    main()
