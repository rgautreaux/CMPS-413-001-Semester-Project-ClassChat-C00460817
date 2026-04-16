from socket import socket, AF_INET, SOCK_STREAM
import select
import sys

serverName = 'localhost' #Server Name
serverPort = 12000 #Port Number
clientSocket = socket(AF_INET, SOCK_STREAM) #TCP Client Socket
clientSocket.connect((serverName,serverPort)) #Socket Connection

username = input('Input your Username:') #User/Client Input
clientSocket.send(username.encode()) #Send username to server

while True:
    readable, writable, exceptional = select.select([sys.stdin, clientSocket], [], []) #Wait for server response
    for currentSocket in readable:
        if currentSocket == clientSocket: 
            #If server response is received
            message = clientSocket.recv(1024) #Receive server response
            if not message:
                print('Connection terminated by the server. Disconnecting...') #Print message if connection is closed by server
                clientSocket.close() #Close Client Socket
                sys.exit() #Exit program
            print('From ClassChat Server: ', message.decode()) #Print server response
        else: 
            #If user input is received
            message = sys.stdin.readline() #User/Client Input
            clientSocket.send(message.encode()) #Send user input to server
