from socket import socket, AF_INET, SOCK_STREAM
import threading
import sys

#Server Message Receiving Thread
def receive_messages(sock: socket) -> None:
    while True:
        message = sock.recv(1024) #Receive server response
        if not message:
            print('\n[System] Connection terminated by the server. Disconnecting...')
            sock.close()
            sys.exit()
        print(f'\n{message.decode()}\n> ', end='', flush=True)  # Add newline and prompt

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
    message = input('> ')
    if message.strip() == "":
        continue
    if message.strip().lower() == "exit":
        print("[System] Disconnecting from server...")
        clientSocket.close()
        sys.exit()
    clientSocket.send(message.encode()) #Send message to server