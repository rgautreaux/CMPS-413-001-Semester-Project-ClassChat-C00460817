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
client_dictionary: dict[socket, str] = {}
clients_lock: threading.Lock = threading.Lock()

def broadcast_message(message: str, sender_socket: socket) -> None:
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(json.dumps({"status": "sender", "receiver": message}).encode()) #Send JSON message to client
                except Exception:
                    pass

def handle_client(connectionSocket: socket, addr: Tuple[str, int], username: str) -> None:
    username = "<unknown>"  # Initialize before try
    try:
        username = connectionSocket.recv(1024).decode() # Expecting the first message to be the username
        print(f"Received from client {addr}: {username}") # Log the username received from the client
        client_dictionary[connectionSocket] = username # Add the client and their username to the dictionary
        
        broadcast_message(f"{username} has joined the chat.", connectionSocket) # Notify other clients about the new user
        connectionSocket.send("ACK: Connection Established.".encode()) # Send acknowledgment to the client that the connection is established
        connectionSocket.send("To message a specific user, type '@username message'. To message all users, just type your message.".encode())
        connectionSocket.send("Type 'exit' to disconnect from the server.".encode())
        while True: # Continuously listen for messages from the client
            message = connectionSocket.recv(1024) # Receive a message from the client
            if not message: 
                break # If the client has disconnected, exit the loop
            message_parse = json.loads(message.decode()) # Attempt to parse the message as JSON 

            if "receiver" in message_parse and message_parse["receiver"] in client_dictionary.values(): # Check if the message is intended for a specific recipient
                if message_parse["receiver"] == username: # If the message is intended for this client, send it directly to them
                    client_dictionary[connectionSocket].send(json.dumps({"status": "sender", "receiver": message_parse["receiver"], "text": message_parse["text"]}).encode()) # Send the message to the intended recipient
                    print(f"Received from {username}@{addr}: {message_parse['sender']}: {message_parse['text']}") # Log the message received from the client
                else:
                    pass # If the intended recipient is not this client, do not send the message to this client
            else: #If not intended for a specific person, broadcast message to all active users
                broadcast_message(f"{username}: {json.dumps({"status": "sender", "receiver": message_parse["receiver"], "text": message_parse["text"]})}", connectionSocket) # Broadcast the message to all other clients
    except Exception as e:
        print(f"An error occurred while handling client {addr}: {e}") # Log any exceptions that occur while handling the client

    finally:
        with clients_lock: # Ensure thread-safe access to the clients list when removing the client
            if connectionSocket in clients: 
                clients.remove(connectionSocket) # Remove the client from the list of connected clients
        broadcast_message(f"{username}@{addr} has left the chat.", connectionSocket) # Notify other clients that this user has left the chat
        client_dictionary.pop(connectionSocket, None) # Remove the client and their username from the dictionary
        connectionSocket.close()
        print(f"Connection with client {addr} closed.") # Log that the connection with the client has been closed

while True:
    connectionSocket, addr = serverSocket.accept() # Wait for a new client to connect
    with clients_lock: 
        clients.append(connectionSocket) # Add the new client to the list of connected clients
    threading.Thread(target=handle_client, args=(connectionSocket, addr), daemon=True).start() # Start a new thread to handle the client's communication with the server