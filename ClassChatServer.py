from socket import socket, AF_INET, SOCK_STREAM
serverPort = 12000 #Port Number
serverSocket = socket(AF_INET,SOCK_STREAM) #Server Socket
serverSocket.bind(('',serverPort)) #Binding Socket to Port
serverSocket.listen(5) #Listens for Client Connection
print('The ClassChat Server is ready.') #Print Message/Acknowledgement while waiting for client

clients = [] #List to keep track of connected clients
threads = [] #List to keep track of client threads

while True:
    connectionSocket, addr = serverSocket.accept() #Accepts Connection from Client
    clients.append(connectionSocket) #Adds Client Socket to List of Connected Clients
    newthread = threading.Thread(target=handle_client, args=(connectionSocket,)).start() #Start thread to handle client communication
    threading.Lock(newthread) #Lock to keep main thread alive while receiving messages
    threads.append(newthread)
    
    welcome = connectionSocket.recv(1024).decode() #Receives Welcome Message from Client
    print(f"Received from client {addr}: {welcome}") #Prints Welcome Message from Client
    connectionSocket.send("ACK: Connection Established.".encode()) #Sends Acknowledgement Message to Client    
    
    def broadcast_message(message: str, sender_socket: socket) -> None:
        for client in clients:
            if client != sender_socket:
                client.send(message.encode())

    # Loop to handle multiple messages from the same client
    while True:
        threading.Thread() #Thread to keep main thread alive while receiving messages
        threading.Lock() #Lock to keep main thread alive while receiving messages
        
        data = connectionSocket.recv(1024) #Receives Message from Client
        if not data:   #If no data is received, the client has disconnected
            print("Client disconnected.") #Print message indicating client disconnection
            clients.remove(connectionSocket) #Remove client from list of connected clients
            threads.remove(newthread) #Remove thread from list of client threads
            connectionSocket.close() #Close the client socket
            break #Exit loop to close connection and wait for new clients
        
        message = data.decode() #Decode message from client
        print(f"Received from client {addr}: {message}") #Print message received from client
        connectionSocket.send(message.upper().encode()) #Sends back the message in uppercase to the client as a response

    connectionSocket.close()