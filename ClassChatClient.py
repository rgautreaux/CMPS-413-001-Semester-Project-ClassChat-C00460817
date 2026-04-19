from socket import socket, AF_INET, SOCK_STREAM
import threading
import sys
import json
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def receive_messages(sock: socket) -> None:
    while True:
        message = sock.recv(1024) #Receive server response
        if not message: #If the server has closed, exit loop and close the socket
            print('\n[System] Connection terminated by the server. Disconnecting...')
            sock.close()
            sys.exit()

        try:
            inc_msg = json.loads(message.decode()) #Attempt to parse the incoming message as JSON
            status = inc_msg.get("status")
            if status == "ACK":
                print(f'\n[System] {inc_msg.get("message")}')
            elif status == "error":
                print(f'\n[Error] {inc_msg.get("text")}')
            elif status == "info":
                info_text = inc_msg.get("text", "").strip()
                if info_text:
                    print(f'\n[Info] {info_text}')
            elif inc_msg.get("type") == "group_message":
                group = inc_msg.get("group")
                sender = inc_msg.get("sender")
                text = inc_msg.get("text")
                print(f"\n[{group}] {sender}: {text}")
            elif inc_msg.get("type") == "file_transfer":
                sender = inc_msg.get("sender")
                file_name = inc_msg.get("filename")
                file_data = inc_msg.get("filedata")
                print(f"\n[File Transfer] {sender} sent a file '{file_name}' with data: {file_data}")
                save = input(f"Do you want to save '{file_name}'? (y/n): ").strip().lower()
                if save == "y":
                    try:
                        with open(file_name, "wb") as file_out:
                            file_out.write(base64.b64decode(file_data))
                        print(f"[System] File '{file_name}' saved successfully.")
                    except Exception as e:
                        print(f"[Error] Failed to save file: {e}")
                else:
                    print("[System] File not saved.")
            elif inc_msg.get("type") == "encrypted":
                sender = inc_msg.get("sender")
                encrypted_text = base64.b64decode(inc_msg.get("text"))
                iv_val = base64.b64decode(inc_msg.get("iv"))
                cipher_obj = Cipher(algorithms.AES(session_key), modes.CFB(iv_val))
                decryptor = cipher_obj.decryptor()
                decrypted_text = decryptor.update(encrypted_text) + decryptor.finalize()
                print(f"\n[Decrypted Message] {sender}: {decrypted_text.decode()}")
            elif inc_msg.get("type") == "offline_message":
                sender = inc_msg.get("sender")
                text = inc_msg.get("text")
                print(f"\n[Offline Message] {sender}: {text}")
            else:
                sender = inc_msg.get("sender", "Unknown")
                text = inc_msg.get("text", "")
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

server_public_key = None
session_key = None

#Username Input and Sending to Server
user_name = input('Input your Username:') #User/Client Input
clientSocket.send(user_name.encode()) #Send username to server

# Receive server's public key
while True:
    srv_msg = clientSocket.recv(4096)
    srv_incoming = json.loads(srv_msg.decode())
    if srv_incoming.get("text") == "send_messagePUBLIC_KEY":
        server_public_key = serialization.load_pem_public_key(srv_incoming.get("key").encode())
        break

# Generate AES session key
session_key = os.urandom(32)  # 256-bit key
encrypted_session_key = server_public_key.encrypt(
    session_key,
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)
clientSocket.send(json.dumps({"type": "session_key", "key": base64.b64encode(encrypted_session_key).decode()}).encode())

#Message Receiving Thread
threading.Thread(target=receive_messages, args=(clientSocket,), daemon=True).start() #Start thread to receive server messages
while True:
    print("To message a specific user, type '@username message'. To message all users, just type your message.")
    print("Type 'exit' to disconnect from the server.")
    msg_type = input('Message Type (Group, Private, File_Transfer, Offline_Message, Encrypted): ').strip() #User/Client Input for recipient of message
    if not msg_type:
        msg_type = "broadcast"
    if msg_type.lower() == "group": #User/Client Input for group command or message
        group_input = input('Group Command (Command or Message): ').strip()
        if group_input.lower() == "command": #If the user wants to send a group command
            command = input('Group Command (Create, Join, Leave, List): ').strip() #User/Client Input for group command type
            group_name = input('Group Name: ').strip() if command.lower() in ["create", "join", "leave"] else ""
            group_cmd = {
                "type": "group_command",
                "command": command.lower(),
                "group": group_name,
                "sender": user_name
            }
            clientSocket.send(json.dumps(group_cmd).encode())
            continue 
        elif group_input.lower() == "message": #If the user wants to send a group message
            group_name = input('Group Name: ').strip()
            group_message = input('Group Message: ').strip() #User/Client Input for group message text
            group_msg = {
                "type": "group_message",
                "group": group_name,
                "sender": user_name,
                "text": group_message
            }
            clientSocket.send(json.dumps(group_msg).encode())
            continue
    elif msg_type.lower() == "file_transfer":
        receiver = input('To (username): ').strip() #User/Client Input for recipient of file
        if not receiver:
            continue
        file_name = input('Filename: ').strip() #User/Client Input for filename if message type is file transfer
        if not file_name:
            continue
        try:
            with open(file_name, "rb") as file_in:
                file_data = base64.b64encode(file_in.read()).decode()
        except Exception as e:
            print(f"[Error] Could not read file: {e}")
            continue
        if file_data.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        file_msg = {
            "type": "file_transfer",
            "sender": user_name,
            "receiver": receiver,
            "filename": file_name,
            "filedata": file_data
        }
        clientSocket.send(json.dumps(file_msg).encode())
        continue
    elif msg_type.lower() == "offline_message":
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
            "sender": user_name,
            "receiver": receiver,
            "text": offline_message
        }
        clientSocket.send(json.dumps(offline_msg).encode())
        continue
    elif msg_type.lower() == "encrypted":
        plaintext = input('Encrypted Message: ').strip()
        if not plaintext:
            continue
        iv_val = os.urandom(16)
        cipher_obj = Cipher(algorithms.AES(session_key), modes.CFB(iv_val))
        encryptor = cipher_obj.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        encrypted_msg = {
            "type": "encrypted",
            "sender": user_name,
            "iv": base64.b64encode(iv_val).decode(),
            "text": base64.b64encode(ciphertext).decode()
        }
        clientSocket.send(json.dumps(encrypted_msg).encode())
        continue
    elif msg_type.lower() == "private":
        receiver = input('To (username): ').strip() #User/Client Input for recipient of message
        if not receiver:
            continue
        message_text = input('Message: ').strip() #User/Client Input for message to send
        if not message_text:
            continue
        if message_text.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        private_msg = {
            "type": "private_message",
            "sender": user_name,
            "receiver": receiver,
            "text": message_text
        }
        clientSocket.send(json.dumps(private_msg).encode())
        continue
    elif msg_type.lower() == "broadcast":
        receiver = input('To (username or "all"): ').strip() #User/Client Input for recipient of message
        if not receiver:
            receiver = "all"
        message_text = input('Message: ').strip() #User/Client Input for message to send
        if not message_text:
            continue
        if message_text.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            clientSocket.close()
            sys.exit()
        msg = {
            "type": "broadcast",
            "sender": user_name,
            "receiver": "all",
            "text": message_text
        }
        clientSocket.send(json.dumps(msg).encode())
        continue

def send_group_message_to_user(target_user: str, group_name: str, sender: str, message: str):
    group_msg = {
        "type": "group_message",
        "group": group_name,
        "sender": sender,
        "text": message
    }
    clientSocket.send(json.dumps(group_msg).encode())
