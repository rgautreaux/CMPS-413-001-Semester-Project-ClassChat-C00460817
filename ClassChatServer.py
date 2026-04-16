from socket import socket, AF_INET, SOCK_STREAM
serverPort = 12000 #Port Number
serverSocket = socket(AF_INET,SOCK_STREAM) #Server Socket
serverSocket.bind(('',serverPort)) #Binding Socket to Port
serverSocket.listen(5) #Listens for Client Connection
print('The ClassChat Server is ready.') #Print Message/Acknowledgement while waiting for client

clients = [] #List to keep track of connected clients

while True:
    connectionSocket, addr = serverSocket.accept() #Accepts Connection from Client
    clients.append(connectionSocket) #Adds Client Socket to List of Connected Clients
    welcome = connectionSocket.recv(1024).decode() #Receives Welcome Message from Client
    print(f"Received from client: {welcome}") #Prints Welcome Message from Client
    connectionSocket.send("ACK: Connection Established.".encode()) #Sends Acknowledgement Message to Client

    # Loop to handle multiple messages from the same client
    while True:
        data = connectionSocket.recv(1024)
        if not data:
            print("Client disconnected.")
            break
        message = data.decode()
        print(f"Received from client: {message}")
        connectionSocket.send(message.upper().encode())

    connectionSocket.close()