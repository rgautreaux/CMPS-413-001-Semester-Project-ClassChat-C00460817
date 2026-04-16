from socket import socket, AF_INET, SOCK_STREAM
import threading
import sys

#Server Message Receiving Thread
def receive_messages(sock: socket) -> None:
    while True:
        message = sock.recv(1024) #Receive server response
        threading.Thread(target=receive_messages, args=(clientSocket,), daemon=True).start() #Start thread to receive server messages
        threading.Lock() #Lock to keep main thread alive while receiving messages
        if not message:
            print('Connection terminated by the server. Disconnecting...') #Print message if connection is closed by server
            sock.close() #Close Client Socket
            sys.exit() #Exit program
        print('From ClassChat Server: ', message.decode()) #Print server response

serverName = 'localhost' #Server Name
serverPort = 12000 #Port Number
clientSocket = socket(AF_INET, SOCK_STREAM) #TCP Client Socket
clientSocket.connect((serverName,serverPort)) #Socket Connection


#Username Input and Sending to Server
username = input('Input your Username:') #User/Client Input
clientSocket.send(username.encode()) #Send username to server

#Message Receiving Thread
threading.Thread(target=receive_messages, args=(clientSocket,), daemon=True).start() #Start thread to receive server messages
threading.Lock() #Lock to keep main thread alive while receiving messages
while True:
    message = input('Enter message to send to ClassChat Server (type "exit" to leave):')
    if message.strip() == "":
        continue  # Ignore empty messages
    if message.strip().lower() in ("exit"):
        print("Disconnecting from server...")
        clientSocket.close()
        sys.exit()
    clientSocket.send(message.encode()) #Send message to server