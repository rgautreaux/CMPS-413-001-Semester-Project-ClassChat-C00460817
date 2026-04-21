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
from tkinter import scrolledtext, filedialog, simpledialog, messagebox
import threading
import socket
import json
import base64
import os

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
class ClassChatClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("ClassChat Client")
        self.chat_area = scrolledtext.ScrolledText(master, state=tk.DISABLED, width=60, height=20)
        self.chat_area.pack(padx=10, pady=10)
        self.entry_message = tk.Entry(master, width=40)
        self.entry_message.pack(side=tk.LEFT, padx=(10,0), pady=(0,10))
        self.entry_message.bind("<Return>", self.send_message)
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))
        # Add more buttons/menus for group, file, etc.
        # Example: self.group_button = tk.Button(master, text="Group", command=self.group_command)
        # self.group_button.pack(...)

        # Socket setup, encryption, etc.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 12000))
        # ... (username, key exchange, etc.)

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, event=None):
        msg = self.entry_message.get()
        if msg:
            # Here, build the correct JSON for the message type
            # Example: send a broadcast
            message_json = json.dumps({
                "type": "broadcast",
                "sender": self.username,
                "receiver": "all",
                "text": msg
            })
            self.sock.send(message_json.encode())
            self.entry_message.delete(0, tk.END)

    def send_private_message(self):
        recipient = simpledialog.askstring("Private Message", "Recipient username:", parent=self.master)
        if not recipient:
            return
        msg = self.entry_message.get()
        if msg:
            message_json = json.dumps({
                "type": "private_message",
                "sender": self.username,
                "receiver": recipient,
                "text": msg
            })
            self.sock.send(message_json.encode())
            self.entry_message.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                # Parse and display message
                try:
                    msg = json.loads(data.decode())
                    # Format and display in chat_area
                    self.display_message(msg)
                except Exception:
                    self.display_message({"text": data.decode()})
            except Exception:
                break

    def display_message(self, msg):
        self.chat_area.config(state=tk.NORMAL)
        # Format message based on type
        if msg.get("type") == "group_message":
            display = f"[{msg['group']}] {msg['sender']}: {msg['text']}\n"
        elif msg.get("type") == "private_message":
            display = f"[Private] {msg['sender']} to {msg['receiver']}: {msg['text']}\n"
        elif msg.get("type") == "file_transfer":
            display = f"[File] {msg['sender']} sent '{msg['filename']}'\n"
            # Prompt to save file, etc.
        else:
            display = f"{msg.get('sender', '')}: {msg.get('text', '')}\n"
        self.chat_area.insert(tk.END, display)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def group_command(self):
        command = simpledialog.askstring("Group Command", "Enter command (create/join/leave/list):", parent=self.master)
        group = simpledialog.askstring("Group Name", "Enter group name:", parent=self.master) if command in ["create", "join", "leave"] else ""
        if command:
            group_cmd = {
                "type": "group_command",
                "command": command,
                "group": group,
                "sender": self.username
            }
            self.sock.send(json.dumps(group_cmd).encode())

    def send_group_message(self):
        group = simpledialog.askstring("Group Name", "Enter group name:", parent=self.master)
        msg = self.entry_message.get()
        if group and msg:
            group_msg = {
                "type": "group_message",
                "group": group,
                "sender": self.username,
                "text": msg
            }
            self.sock.send(json.dumps(group_msg).encode())
            self.entry_message.delete(0, tk.END)

    def send_file(self):
        receiver = simpledialog.askstring("File Transfer", "Recipient username:", parent=self.master)
        file_path = filedialog.askopenfilename()
        if receiver and file_path:
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode()
            file_msg = {
                "type": "file_transfer",
                "sender": self.username,
                "receiver": receiver,
                "filename": os.path.basename(file_path),
                "filedata": file_data
            }
            self.sock.send(json.dumps(file_msg).encode())

    def send_offline_message(self):
        receiver = simpledialog.askstring("Offline Message", "Recipient username:", parent=self.master)
        msg = self.entry_message.get()
        if receiver and msg:
            offline_msg = {
                "type": "offline_message",
                "sender": self.username,
                "receiver": receiver,
                "text": msg
            }
            self.sock.send(json.dumps(offline_msg).encode())
            self.entry_message.delete(0, tk.END)

    def send_encrypted_message(self):
        msg = self.entry_message.get()
        if msg:
            iv_val = os.urandom(16)
            cipher_obj = Cipher(algorithms.AES(self.session_key), modes.CFB(iv_val))
            encryptor = cipher_obj.encryptor()
            ciphertext = encryptor.update(msg.encode()) + encryptor.finalize()
            encrypted_msg = {
                "type": "encrypted",
                "sender": self.username,
                "iv": base64.b64encode(iv_val).decode(),
                "text": base64.b64encode(ciphertext).decode()
            }
            self.sock.send(json.dumps(encrypted_msg).encode())
            self.entry_message.delete(0, tk.END)

root = tk.Tk()
app = ClassChatClientGUI(root)
root.mainloop()
