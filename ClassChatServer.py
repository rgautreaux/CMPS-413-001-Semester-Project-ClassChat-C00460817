from socket import socket, AF_INET, SOCK_STREAM
serverPort = 12000 #Port Number
serverSocket = socket(AF_INET,SOCK_STREAM) #Server Socket
serverSocket.bind(('',serverPort)) #Binding Socket to Port
serverSocket.listen(5) #Listens for Client Connection
print('The ClassChat Server is ready.') #Print Message/Acknowledgement while waiting for client

while True:
    connectionSocket, addr = serverSocket.accept()
    welcome = connectionSocket.recv(1024).decode()
    connectionSocket.send("ACK: Connection Established.".encode())

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