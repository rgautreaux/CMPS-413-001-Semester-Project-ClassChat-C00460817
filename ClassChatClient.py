from email import message
from socket import socket, AF_INET, SOCK_STREAM
import threading
import sys
import json

#Server Message Receiving Thread
def receive_messages(sock: socket) -> None:
    while True:
        message = sock.recv(1024) #Receive server response
        if not message: #If the server has closed, exit loop and close the socket
            print('\n[System] Connection terminated by the server. Disconnecting...')
            sock.close()
            sys.exit()

        try:
            incoming_message = json.loads(message.decode()) #Attempt to parse the incoming message as JSON
            status = incoming_message.get("status")
            # Print each message on its own line, with clear prefixes
            if status == "ACK":
                print(f'\n[System] {incoming_message.get("message")}')
            elif status == "error":
                print(f'\n[Error] {incoming_message.get("text")}')
            elif status == "info":
                # Only print non-empty info messages
                info_text = incoming_message.get("text", "").strip()
                if info_text:
                    print(f'\n[Info] {info_text}')
            else:
                # Regular chat message
                sender = incoming_message.get("sender", "Unknown") # Default to "Unknown" if sender is not provided
                text = incoming_message.get("text", "") # Default to empty string if text is not provided
                print(f'\n{sender}: {text}')
            print("> ", end='', flush=True) # Always print prompt after message
        except Exception:
            # If the message cannot be parsed as JSON, print it as a regular message from the server
            print(f'\n{message.decode()}')
            print("> ", end='', flush=True)

serverName = 'localhost' #Server Name
serverPort = 12000 #Port Number
clientSocket = socket(AF_INET, SOCK_STREAM) #TCP Client Socket
clientSocket.connect((serverName,serverPort)) #Socket Connection


#Username Input and Sending to Server
username = input('Input your Username:') #User/Client Input
clientSocket.send(username.encode()) #Send username to server


#Message Receiving Thread
threading.Thread(target=receive_messages, args=(clientSocket,), daemon=True).start() #Start thread to receive server messages
while True:
    print("To message a specific user, type '@username message'. To message all users, just type your message.")
    print("Type 'exit' to disconnect from the server.")
    type = input('Message Type (Group, Private, File Transfer, Offline, Encrypted): ').strip() #User/Client Input for recipient of message
    if not type:
        type = "broadcast"
    if type.lower() == "group":
        group_input = input('Group Command (Command or Message): ').strip() #User/Client Input for group message type
        if group_input.lower() == "command":
            command = input('Group Command (Create, Join, Leave, List): ').strip() #User/Client Input for group command if message type is group command
            if not command:
                continue
            if command.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        if group_input.lower() == "message":
            group_message = input('Group Message: ').strip() #User/Client Input for group command if message type is group command
            if not group_message:
                continue
            if group_message.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
    elif type.lower() == "file transfer":
        filename = input('Filename: ').strip() #User/Client Input for filename if message type is file transfer
        if not filename:
            continue
        filedata = input('File Data (base64-encoded): ').strip() #User/Client Input for file data if message type is file transfer
        if not filedata:
            continue
        if filedata.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
    elif type.lower() == "offline message":
        offline_message = input('Offline Message: ').strip() #User/Client Input for offline message if message type is offline message
        if not offline_message:
            continue
        if offline_message.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
    elif type.lower() == "encrypted":
        encrypted_message = input('Encrypted Message: ').strip() #User/Client Input for encrypted message if message type is encrypted
        if not encrypted_message:
            continue
        if encrypted_message.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
    elif type.lower() == "private":
        receiver = input('To (username): ').strip() #User/Client Input for recipient of message
        if not receiver:
            receiver = "all"
        messageText = input('Message: ').strip() #User/Client Input for message to send
        if not messageText:
            continue
        if messageText.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
    else:
        receiver = input('To (username): ').strip() #User/Client Input for recipient of message
        if not receiver:
            receiver = "all"
        messageText = input('Message: ').strip() #User/Client Input for message to send
        if not messageText:
            continue
        if messageText.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
    #JSON Broadcast Message Format Parsing and Sending to Server
    msg = {
        "status": "1",
        " type " : "broadcast",
        "sender": username,
        "text": messageText
    }
    clientSocket.send(json.dumps(msg).encode())

    #JSON Private Message Format Parsing and Sending to Server
    private_msg = {
        "status": "1",
        " type " : "private_message" ,
        "sender": username,
        "receiver": receiver,
        "text": messageText
    }
    clientSocket.send(json.dumps(private_msg).encode())

    #JSON Group Message Format Parsing and Sending to Server
    group_msg = {
        "status": "1",
        " type " :  type,
        "sender": username,
        "receiver": "groupname",
        " group ": "groupname", 
        "text": messageText
    }
    clientSocket.send(json.dumps(group_msg).encode())


     #JSON Group Message Format Parsing and Sending to Server
    group_msg = {
        "status": "1",
        " type " :  type,
        "sender": username,
        "receiver": "groupname",
        " group ": "groupname", 
        " command ": "create" | "join" | "leave" | "list",
        "text": messageText
    }
    clientSocket.send(json.dumps(group_msg).encode())

    #JSON File Transfer Message Format Parsing and Sending to Server
    file_msg = {
        "status": "1",
        " type " :  type,
        "sender": username,
        "receiver": " receiver " | "groupname",
        " group ": "groupname", 
        " filename ": "example.txt",
        " filedata ": "<base64-encoded>",
        "text": messageText
    }
    clientSocket.send(json.dumps(file_msg).encode())

    #JSON Offline Message Format Parsing and Sending to Server
    offline_msg = {
        "status": "1",
        " type " :  type,
        "sender": username,
        "receiver": " receiver " | "groupname",
        " group ": "groupname", 
        " filename ": "example.txt",
        " filedata ": "<base64-encoded>",
        "text": messageText
    }
    clientSocket.send(json.dumps(offline_msg).encode())

    #JSON Encrypted Message Format Parsing and Sending to Server
    encrypted_msg = {
        "status": "1",
        " type " :  type,
        "sender": username,
        "receiver": " receiver " | "groupname",
        " group ": "groupname", 
        " filename ": "example.txt",
        " filedata ": "<base64-encoded>",
        "text": messageText
    }
    clientSocket.send(json.dumps(encrypted_msg).encode())