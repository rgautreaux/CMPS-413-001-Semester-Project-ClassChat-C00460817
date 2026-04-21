from socket import socket, AF_INET, SOCK_STREAM
import threading
import sys
import json
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import tkinter as tk
from tkinter import scrolledtext
import threading
import socket
import json

ddef receive_messages():
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            # If you use JSON, decode here
            # msg = json.loads(data.decode())
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, data.decode() + '\n')
            chat_area.config(state=tk.DISABLED)
            chat_area.see(tk.END)
        except Exception:
            break





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
    if srv_incoming.get("text") == "SERVER_PUBLIC_KEY":
        server_public_key = serialization.load_pem_public_key(srv_incoming.get("key").encode())
        break

# Generate AES session key
session_key = os.urandom(32)  # 256-bit key
if isinstance(server_public_key, RSAPublicKey):
    encrypted_session_key = server_public_key.encrypt(
        session_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    clientSocket.send(json.dumps({"type": "session_key", "key": base64.b64encode(encrypted_session_key).decode()}).encode())
else:
    print("[Error] Server public key is not a valid RSA public key.")
    sys.exit(1)


# --- Tkinter GUI Setup ---
def send_message():
    msg = entry_message.get()
    if msg:
        # Example: send as plain text or JSON
        client_socket.send(msg.encode())
        entry_message.delete(0, tk.END)

#Message Receiving Thread
root = tk.Tk()
root.title("ClassChat Client")

chat_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, width=50, height=20)
chat_area.pack(padx=10, pady=10)

entry_message = tk.Entry(root, width=40)
entry_message.pack(side=tk.LEFT, padx=(10,0), pady=(0,10))
entry_message.bind("<Return>", lambda event: send_message())

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))

# Start the receiving thread
threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()

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
            if command.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
                print("[System] Disconnecting from server...")
                disconnect_message = json.dumps({"type": "disconnect"})
                clientSocket.send(disconnect_message.encode())
                clientSocket.close()
                sys.exit()
            group_name = input('Group Name: ').strip() if command.lower() in ["create", "join", "leave"] else ""
            if group_name.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
                print("[System] Disconnecting from server...")
                disconnect_message = json.dumps({"type": "disconnect"})
                clientSocket.send(disconnect_message.encode())
                clientSocket.close()
                sys.exit()
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
            if group_name.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
                print("[System] Disconnecting from server...")
                disconnect_message = json.dumps({"type": "disconnect"})
                clientSocket.send(disconnect_message.encode())
                clientSocket.close()
                sys.exit()
            group_message = input('Group Message: ').strip() #User/Client Input for group message text
            if group_message.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
                print("[System] Disconnecting from server...")
                disconnect_message = json.dumps({"type": "disconnect"})
                clientSocket.send(disconnect_message.encode())
                clientSocket.close()
                sys.exit()
            group_msg = {
                "type": "group_message",
                "group": group_name,
                "sender": user_name,
                "text": group_message
            }
            clientSocket.send(json.dumps(group_msg).encode())
            continue
        elif group_input.lower() == "exit": #If the user wants to exit now, let them exit
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
            clientSocket.close()
            sys.exit()
    elif msg_type.lower() == "file_transfer":
        receiver = input('To (username): ').strip() #User/Client Input for recipient of file
        if not receiver:
            continue
        elif receiver.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
            clientSocket.close()
            sys.exit()
        file_name = input('Filename: ').strip() #User/Client Input for filename if message type is file transfer
        if not file_name:
            continue
        elif file_name.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
            clientSocket.close()
            sys.exit()
        try:
            with open(file_name, "rb") as file_in:
                file_data = base64.b64encode(file_in.read()).decode()
        except Exception as e:
            print(f"[Error] Could not read file: {e}")
            continue
        if file_data.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
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
        elif receiver.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
            clientSocket.close()
            sys.exit()
        offline_message = input('Offline Message: ').strip() #User/Client Input for offline message if message type is offline message
        if not offline_message:
            continue
        elif offline_message.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
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
        if plaintext.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
            clientSocket.close()
            sys.exit()
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
        elif receiver.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
            clientSocket.close()
            sys.exit()
        message_text = input('Message: ').strip() #User/Client Input for message to send
        if not message_text:
            continue
        elif message_text.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
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
        elif receiver.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
            clientSocket.close()
            sys.exit()
        message_text = input('Message: ').strip() #User/Client Input for message to send
        if not message_text:
            continue
        elif message_text.strip().lower() == "exit": # If the user types "exit", close the connection and exit the program
            print("[System] Disconnecting from server...")
            disconnect_message = json.dumps({"type": "disconnect"})
            clientSocket.send(disconnect_message.encode())
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
    elif msg_type.strip().lower() == "exit": # If the user types "exit" at the message type prompt, close the connection and exit the program
        print("[System] Disconnecting from server...")
        disconnect_message = json.dumps({"type": "disconnect"})
        clientSocket.send(disconnect_message.encode())
        clientSocket.close()
        sys.exit()

def send_group_message_to_user(group: str, sender: str, message: str):
    group_message_obj = {
        "type": "group_message",
        "group": group,
        "sender": sender,
        "text": message
    }
    clientSocket.send(json.dumps(group_message_obj).encode())
