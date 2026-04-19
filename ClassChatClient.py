from socket import socket, AF_INET, SOCK_STREAM
import threading
import sys
import json
import base64
import cryptography

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
            if status == "ACK":
                print(f'\n[System] {incoming_message.get("message")}')
            elif status == "error":
                print(f'\n[Error] {incoming_message.get("text")}')
            elif status == "info":
                info_text = incoming_message.get("text", "").strip()
                if info_text:
                    print(f'\n[Info] {info_text}')
            elif incoming_message.get("type") == "group_message":
                group = incoming_message.get("group")
                sender = incoming_message.get("sender")
                text = incoming_message.get("text")
                print(f"\n[{group}] {sender}: {text}")
            elif incoming_message.get("type") == "file_transfer":
                sender = incoming_message.get("sender")
                filename = incoming_message.get("filename")
                filedata = incoming_message.get("filedata")
                print(f"\n[File Transfer] {sender} sent a file '{filename}' with data: {filedata}")
                save = input(f"Do you want to save '{filename}'? (y/n): ").strip().lower()
                if save == "y":
                    try:
                        with open(filename, "wb") as f:
                            f.write(base64.b64decode(filedata))
                        print(f"[System] File '{filename}' saved successfully.")
                    except Exception as e:
                        print(f"[Error] Failed to save file: {e}")
                else:
                    print("[System] File not saved.")
            else:
                sender = incoming_message.get("sender", "Unknown")
                text = incoming_message.get("text", "")
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
    type = input('Message Type (Group, Private, File_Transfer, Offline_Message, Encrypted): ').strip() #User/Client Input for recipient of message
    if not type:
        type = "broadcast"
    if type.lower() == "group": #User/Client Input for group command or message
        group_input = input('Group Command (Command or Message): ').strip()
        if group_input.lower() == "command": #If the user wants to send a group command
            command = input('Group Command (Create, Join, Leave, List): ').strip() #User/Client Input for group command type
            groupname = input('Group Name: ').strip() if command.lower() in ["create", "join", "leave"] else ""
            group_cmd = {
                "type": "group_command",
                "command": command.lower(),
                "group": groupname,
                "sender": username
            }
            clientSocket.send(json.dumps(group_cmd).encode())
            continue 
        elif group_input.lower() == "message": #If the user wants to send a group message
            groupname = input('Group Name: ').strip()
            group_message = input('Group Message: ').strip() #User/Client Input for group message text
            group_msg = {
                "type": "group_message",
                "group": groupname,
                "sender": username,
                "text": group_message
            }
            clientSocket.send(json.dumps(group_msg).encode())
            continue
    elif type.lower() == "file_transfer":
        receiver = input('To (username): ').strip() #User/Client Input for recipient of file
        if not receiver:
            continue
        filename = input('Filename: ').strip() #User/Client Input for filename if message type is file transfer
        if not filename:
            continue
        try:
            with open(filename, "rb") as f:
                filedata = base64.b64encode(f.read()).decode()
        except Exception as e:
            print(f"[Error] Could not read file: {e}")
            continue
        if filedata.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        file_msg = {
            "type": "file_transfer",
            "sender": username,
            "receiver": receiver,
            "filename": filename,
            "filedata": filedata
        }
        clientSocket.send(json.dumps(file_msg).encode())
        continue
    elif type.lower() == "offline_message":
        receiver = input('To (username): ').strip() # Prompt for recipient
        if not receiver:
            continue
        offline_message = input('Offline Message: ').strip() #User/Client Input for offline message if message type is offline message
        if not offline_message:
            continue
        if offline_message.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        offline_msg = {
            "type": "offline_message",
            "sender": username,
            "receiver": receiver,
            "text": offline_message
        }
        clientSocket.send(json.dumps(offline_msg).encode())
        continue
    elif type.lower() == "encrypted":
        encrypted_message = input('Encrypted Message: ').strip() #User/Client Input for encrypted message if message type is encrypted
        if not encrypted_message:
            continue
        if encrypted_message.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        encrypted_msg = {
            "type": "encrypted",
            "sender": username,
            "text": encrypted_message
        }
        clientSocket.send(json.dumps(encrypted_msg).encode())
        continue
    elif type.lower() == "private":
        receiver = input('To (username): ').strip() #User/Client Input for recipient of message
        if not receiver:
            continue
        messageText = input('Message: ').strip() #User/Client Input for message to send
        if not messageText:
            continue
        if messageText.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        private_msg = {
            "type": "private_message",
            "sender": username,
            "receiver": receiver,
            "text": messageText
        }
        clientSocket.send(json.dumps(private_msg).encode())
        continue
    elif type.lower() == "broadcast":
        receiver = input('To (username or "all"): ').strip() #User/Client Input for recipient of message
        if not receiver:
            receiver = "all"
        messageText = input('Message: ').strip() #User/Client Input for message to send
        if not messageText:
            continue
        if messageText.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        msg = {
            "type": "broadcast",
            "sender": username,
            "receiver": "all",
            "text": messageText
        }
        clientSocket.send(json.dumps(msg).encode())
        continue
