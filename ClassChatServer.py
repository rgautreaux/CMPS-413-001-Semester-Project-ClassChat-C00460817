import threading
import json
from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple, List

serverPort = 12000
serverSocket: socket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
print('The ClassChat Server is ready.')

clients: List[socket] = []
client_dictionary: dict[str, socket] = {}
clients_lock: threading.Lock = threading.Lock()

def broadcast_message(message: str, sender_socket: socket) -> None:
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message.encode() if isinstance(message, str) else message)
                except Exception:
                    pass

def handle_client(connectionSocket: socket, addr: Tuple[str, int], username: str) -> None:
    try:
        username = connectionSocket.recv(1024).decode().strip() # Expecting the first message to be the username
        print(f"Received from client {addr}: {username}") # Log the username received from the client
        with clients_lock:
            client_dictionary[username] = connectionSocket # Add the client and their username to the dictionary
            clients.append(connectionSocket) # Add the client to the list of connected clients
        
        broadcast_message(f"{username} has joined the chat.", connectionSocket) # Notify other clients about the new user
        connectionSocket.send(f"Welcome to ClassChat, {username}!".encode()) # Send a welcome message to the new client
        connectionSocket.send(json.dumps({"status": "ACK", "message": "Connection Established."}).encode()) # Send acknowledgment to the client that the connection is established
        connectionSocket.send("To message a specific user, type '@username message'. To message all users, just type your message.".encode())
        connectionSocket.send("Type 'exit' to disconnect from the server.".encode())
        while True: # Continuously listen for messages from the client
            message = connectionSocket.recv(1024) # Receive a message from the client
            if not message: 
                break # If the client has disconnected, exit the loop
                message_parse = json.loads(message.decode()) # Attempt to parse the message as JSON 
                reciever = message_parse.get("receiver", "").strip()
            if reciever and reciever.lower() != "all":
                #Direct Message for intended recipient
                if reciever in client_dictionary:
                    try:
                        client_dictionary[reciever].send(message) # Send the message to the intended recipient
                        print(f"Received from {username}@{addr}: {message_parse['sender']}: {message_parse['text']}") # Log the message received from the client
                    except Exception:
                        pass
                else:
                    error_msg = {"status": "error", "text": f"User '{reciever}' is not online."} # If the intended recipient is not online, let the user know
                    connectionSocket.send(json.dumps(error_msg).encode())
            else: #If not intended for a specific person, broadcast message to all active users
                broadcast_message(message.decode(), connectionSocket)
    except Exception as e:
        print(f"An error occurred while handling client {addr}: {e}") # Log any exceptions that occur while handling the client

    finally:
        with clients_lock: # Ensure thread-safe access to the clients list when removing the client
            if connectionSocket in clients: 
                clients.remove(connectionSocket) # Remove the client from the list of connected clients
            if username in client_dictionary:
                del client_dictionary[username]
        broadcast_message(f"{username}@{addr} has left the chat.", connectionSocket) # Notify other clients that this user has left the chat
        print(f"Connection with client {addr} closed.") # Log that the connection with the client has been closed
        connectionSocket.close()


while True:
    connectionSocket, addr = serverSocket.accept() # Wait for a new client to connect
    with clients_lock: 
        clients.append(connectionSocket) # Add the new client to the list of connected clients
    threading.Thread(target=handle_client, args=(connectionSocket, addr), daemon=True).start() # Start a new thread to handle the client's communication with the server