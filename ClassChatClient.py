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