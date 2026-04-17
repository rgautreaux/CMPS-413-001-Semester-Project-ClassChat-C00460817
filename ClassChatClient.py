from email import message
from email.mime import text
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
            if incoming_message.get("status") == "ACK": #If the message is an acknowledgment
                print(f'\n[System] {incoming_message.get("message")}\n> ', end='', flush=True) #Print the acknowledgment message from the server
            elif incoming_message.get("status") == "error": #If the message is an error message
                print(f'\n[Error] {incoming_message.get("text")}\n> ', end='', flush=True) #Print the error message from the server
            elif incoming_message.get("status") == "info":
                print(f"\n[Info] {incoming_message.get('text')}\n> ", end='', flush=True) #If the message is an informational message (such as a new user logging on ), print it
            else:
                print(f'\n{incoming_message.get("sender")}: {incoming_message.get("text")}\n> ', end='', flush=True) #If the message is a regular chat message, print the sender and the text of the message
        except Exception:
            print(f'\n{message.decode()}\n> ', end='', flush=True) #If the message cannot be parsed as JSON, print it as a regular message from the server



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
    #JSON Message Format Parsing and Sending to Server
    msg = {
        "status": "1",
        "sender": username,
        "receiver": receiver,
        "text": messageText
    }
    clientSocket.send(json.dumps(msg).encode())