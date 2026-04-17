import threading
from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple, List

serverPort = 12000
serverSocket: socket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
print('The ClassChat Server is ready.')

clients: List[socket] = []
clients_lock: threading.Lock = threading.Lock()

def broadcast_message(message: str, sender_socket: socket) -> None:
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message.encode())
                except Exception:
                    pass

def handle_client(connectionSocket: socket, addr: Tuple[str, int]) -> None:
    username = "<unknown>"  # Initialize before try
    try:
        username = connectionSocket.recv(1024).decode()
        print(f"Received from client {addr}: {username}")
        broadcast_message(f"{username} has joined the chat.", connectionSocket)
        connectionSocket.send("ACK: Connection Established.".encode())

        while True:
            message = connectionSocket.recv(1024)
            if not message:
                break
            message = message.decode()
            print(f"Received from {username}@{addr}: {message}")
            broadcast_message(f"{username}: {message}", connectionSocket)
    except Exception as e:
        print(f"An error occurred while handling client {addr}: {e}")
    finally:
        with clients_lock:
            if connectionSocket in clients:
                clients.remove(connectionSocket)
        broadcast_message(f"{username}@{addr} has left the chat.", connectionSocket)
        connectionSocket.close()
        print(f"Connection with client {addr} closed.")

while True:
    connectionSocket, addr = serverSocket.accept()
    with clients_lock:
        clients.append(connectionSocket)
    threading.Thread(target=handle_client, args=(connectionSocket, addr), daemon=True).start()
