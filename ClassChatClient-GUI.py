import socket
import threading
import json
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import tkinter as tk
from tkinter import scrolledtext, filedialog, simpledialog, messagebox

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
        self.private_button = tk.Button(master, text="Private", command=self.send_private_message)
        self.private_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))
        self.group_cmd_button = tk.Button(master, text="Group Command", command=self.group_command)
        self.group_cmd_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))
        self.group_msg_button = tk.Button(master, text="Group Message", command=self.send_group_message)
        self.group_msg_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))
        self.file_button = tk.Button(master, text="Send File", command=self.send_file)
        self.file_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))
        self.offline_button = tk.Button(master, text="Offline Message", command=self.send_offline_message)
        self.offline_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))
        self.encrypted_button = tk.Button(master, text="Encrypted Send", command=self.send_encrypted_message)
        self.encrypted_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))
        self.disconnect_button = tk.Button(master, text="Disconnect", command=self.disconnect)
        self.disconnect_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))

        # Socket setup, encryption, etc.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 12000))
        self.username = simpledialog.askstring("Username", "Enter your username:", parent=self.master)
        self.sock.send(self.username.encode())
        # Key exchange
        srv_msg = self.sock.recv(4096)
        srv_incoming = json.loads(srv_msg.decode())
        if srv_incoming.get("text") == "SERVER_PUBLIC_KEY":
            server_public_key = serialization.load_pem_public_key(srv_incoming.get("key").encode())
        else:
            messagebox.showerror("Error", "Failed to receive server public key.")
            self.master.destroy()
            return
        self.session_key = os.urandom(32)
        if isinstance(server_public_key, RSAPublicKey):
            encrypted_session_key = server_public_key.encrypt(
                self.session_key,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            self.sock.send(json.dumps({"type": "session_key", "key": base64.b64encode(encrypted_session_key).decode()}).encode())
        else:
            messagebox.showerror("Error", "Server public key is not valid.")
            self.master.destroy()
            return
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, event=None):
        msg = self.entry_message.get()
        if msg:
            # Broadcast
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
            
    def display_message(self, msg):
        self.chat_area.config(state=tk.NORMAL)
        # Format message based on type
        if msg.get("type") == "group_message":
            display = f"[{msg['group']}] {msg['sender']}: {msg['text']}\n"
        elif msg.get("type") == "private_message":
            display = f"[Private] {msg['sender']} to {msg['receiver']}: {msg['text']}\n"
        elif msg.get("type") == "file_transfer":
            display = f"[File] {msg['sender']} sent '{msg['filename']}'\n"
            self.chat_area.insert(tk.END, display)
            save = messagebox.askyesno("File Transfer", f"Save file '{msg['filename']}' from {msg['sender']}?")
            if save:
                save_path = filedialog.asksaveasfilename(initialfile=msg['filename'])
                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(base64.b64decode(msg['filedata']))
        else:
            display = f"{msg.get('sender', '')}: {msg.get('text', '')}\n"
        self.chat_area.insert(tk.END, display)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        self.master.after(0, lambda: self.display_message(msg))

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

    def disconnect(self):
        try:
            self.sock.send(json.dumps({"type": "disconnect"}).encode())
            self.sock.close()
        except Exception:
            pass
        self.master.destroy()

root = tk.Tk()
app = ClassChatClientGUI(root)
root.mainloop()
