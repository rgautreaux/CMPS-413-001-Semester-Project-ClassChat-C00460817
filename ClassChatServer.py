from socket import socket, AF_INET, SOCK_STREAM
serverPort = 12000 #Port Number
serverSocket = socket(AF_INET,SOCK_STREAM) #Server Socket
serverSocket.bind(('',serverPort)) #Binding Socket to Port
serverSocket.listen(5) #Listens for Client Connection
print('The ClassChat Server is ready.') #Print Message/Acknowledgement while waiting for client

while True:
    connectionSocket, addr = serverSocket.accept() #Accept Connections from Clients
    username = connectionSocket.recv(1024).decode() #Wait for and receive incoming Client Message(s)
    connectionSocket.send("ACK: Connection Established.".encode()) #Send ACK to Client
    
    input = connectionSocket.recv(1024).decode() #Receive Client Message(s)
    connectionSocket.send(input.upper().encode()) #Send Modified Message to Client

connectionSocket.close() #Close Connection Socket