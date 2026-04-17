import threading
import json
from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple, List

serverPort = 12000
serverSocket: socket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
print('The ClassChat Server is ready.')

clients: List[socket] = [] # List to keep track of connected client sockets
client_dictionary: dict[str, socket] = {} # Dictionary to map usernames to their sockets
clients_lock: threading.Lock = threading.Lock() # Lock to ensure thread-safe access 
groups = {} # Dictionary to map group names to lists of member usernames

def broadcast_message(message: str, sender_socket: socket) -> None:
    with clients_lock: # Ensure thread-safe access to the clients list when broadcasting messages
        for client in clients:
            if client != sender_socket: # Don't send the message back to the sender
                try:
                    client.send(message.encode()) # Send the message to the client, encoding it if it's a string
                except Exception:
                    pass # If there's an error sending the message (e.g., client disconnected), ignore it and continue broadcasting to other clients

def handle_client(connectionSocket: socket, addr: Tuple[str, int]) -> None:  # Removed username argument
    username = "<unknown>"  # Initialize before try to avoid unbound variable
    
    try:
        username = connectionSocket.recv(1024).decode().strip() # Expecting the first message to be the username
        print(f"Received from client {addr}: {username}") # Log the username received from the client
        with clients_lock:
            client_dictionary[username] = connectionSocket # Add the client and their username to the dictionary
            clients.append(connectionSocket) # Add the client to the list of connected clients
        
        # Notify other clients about the new user (as info JSON)
        broadcast_message(json.dumps({"status": "info", "text": f"{username} has joined the chat."}), connectionSocket)
        # Send a welcome message to the new client (as info JSON)
        connectionSocket.send(json.dumps({"status": "info", "text": f"Welcome to ClassChat, {username}!"}).encode())
        connectionSocket.send(json.dumps({"status": "ACK", "message": "Connection Established."}).encode()) # Send acknowledgment to the client that the connection is established
        connectionSocket.send(json.dumps({"status": "info", "text": "To message a specific user, type '@username message'. To message all users, just type your message."}).encode())
        connectionSocket.send(json.dumps({"status": "info", "text": "Type 'exit' to disconnect from the server."}).encode())
        while True: # Continuously listen for messages from the client
            message = connectionSocket.recv(1024) # Receive a message from the client
            if not message: 
                break # If the client has disconnected, exit the loop
            message_parse = json.loads(message.decode()) # Attempt to parse the message as JSON 
            if message_parse.get("type") == "group_command": #checks if the message was a group command
                command = message_parse.get("command")
                groupname = message_parse.get("group")
                sender = message_parse.get("sender")
                if command == "create": # Create and Group Command
                    if groupname not in groups:
                        groups[groupname] = set()
                    groups[groupname].add(sender)
                    connectionSocket.send(json.dumps({"status": "info", "text": f"Group '{groupname}' created and joined."}).encode())
                elif command == "join": # Join Group Command
                    if groupname in groups:
                        groups[groupname].add(sender)
                        connectionSocket.send(json.dumps({"status": "info", "text": f"Joined group '{groupname}'."}).encode())
                    else:
                        connectionSocket.send(json.dumps({"status": "error", "text": f"Group '{groupname}' does not exist."}).encode())
                elif command == "list": # List Group Command
                    if groups:
                        group_list = ", ".join(groups.keys())
                        connectionSocket.send(json.dumps({"status": "info", "text": f"Available groups: {group_list}."}).encode())
                    else:
                        connectionSocket.send(json.dumps({"status": "info", "text": "No groups available."}).encode())
                elif command == "leave": # Leave Group Command
                    if groupname in groups and sender in groups[groupname]:
                        groups[groupname].remove(sender)
                        connectionSocket.send(json.dumps({"status": "info", "text": f"Left group '{groupname}'."}).encode())
                    else:
                        connectionSocket.send(json.dumps({"status": "error", "text": f"You are not in group '{groupname}'."}).encode())
                continue  # Skip further processing for this message
            elif message_parse.get("type") == "group_message":
                groupname = message_parse.get("group")
                sender = message_parse.get("sender")
                text = message_parse.get("text")
                handle_group_message(sender, groupname, text)
                continue  # Skip further processing for this message
            elif message_parse.get("type") == "private_message":
                receiver = message_parse.get("receiver", "").strip()
                if receiver and receiver.lower() != "all":
                    #Direct Message for intended recipient
                    if receiver in client_dictionary:
                        try:
                            # Always send JSON-encoded bytes
                            client_dictionary[receiver].send(json.dumps(message_parse).encode())
                            print(f"Received from {username}@{addr}: {message_parse['sender']}: {message_parse['text']}")
                        except Exception:
                            pass
                    else:
                        error_msg = {"status": "error", "text": f"User '{receiver}' is not online."} # If the intended recipient is not online, let the user know
                        connectionSocket.send(json.dumps(error_msg).encode())
            elif message_parse.get("type") == "broadcast":
                receiver = message_parse.get("receiver", "").strip()
                if receiver and receiver.lower() != "all":
                    broadcast_message(message.decode(), connectionSocket)
            else: #If not intended for a specific person, broadcast message to all active users
                broadcast_message(message.decode(), connectionSocket)
    except Exception as e:
        print(f"An error occurred while handling client {addr}: {e}") # Log any exceptions that occur while handling the client

    finally:
        with clients_lock:
            if connectionSocket in clients:
                clients.remove(connectionSocket)
            if username in client_dictionary:
                del client_dictionary[username]
        # Remove user from all groups
        for group in groups.values():
            group.discard(username)
        broadcast_message(json.dumps({"status": "info", "text": f"{username}@{addr} has left the chat."}), connectionSocket)
        print(f"Connection with client {addr} closed.")
        connectionSocket.close()

def handle_group_message(sender, groupname, message):
    if groupname in groups and sender in groups[groupname]:
        for member in groups[groupname]:
            if member != sender:
                # Send as a group_message type for proper client display
                send_group_message_to_user(member, groupname, sender, message)
    else:
        send_message_to_user(sender, "You are not a member of this group.")

def send_group_message_to_user(username, groupname, sender, message):
    if username in client_dictionary:
        try:
            client_dictionary[username].send(json.dumps({
                "type": "group_message",
                "group": groupname,
                "sender": sender,
                "text": message
            }).encode())
        except Exception:
            pass

def send_message_to_user(username, message):
    if username in client_dictionary:
        try:
            client_dictionary[username].send(json.dumps({"status": "info", "text": message}).encode())
        except Exception:
            pass

while True:
    connectionSocket, addr = serverSocket.accept() # Wait for a new client to connect
    threading.Thread(target=handle_client, args=(connectionSocket, addr), daemon=True).start() # Start a new thread to handle the client's communication with the server