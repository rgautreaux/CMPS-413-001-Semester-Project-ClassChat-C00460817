from socket import socket, AF_INET, SOCK_STREAM


def handle_client(connectionSocket: socket) -> None:
    while True:
        data = connectionSocket.recv(1024) #Receives Message from Client
        if not data:   #If no data is received, the client has disconnected
            print("Client disconnected.") #Print message indicating client disconnection
            clients.remove(connectionSocket) #Remove client from list of connected clients
            thread.remove(newthread) #Remove thread from list of client thread
            connectionSocket.close() #Close the client socket
            break #Exit loop to close connection and wait for new clients
        
        message = data.decode() #Decode message from client
        print(f"Received from client {addr}: {message}") #Print message received from client
        connectionSocket.send(message.upper().encode()) #Sends back the message in uppercase to the client as a response


    def broadcast_message(message: str, sender_socket: socket) -> None:
        for client in clients:
            if client != sender_socket:
                client.send(message.encode())


serverPort = 12000 #Port Number
serverSocket = socket(AF_INET,SOCK_STREAM) #Server Socket
serverSocket.bind(('',serverPort)) #Binding Socket to Port
serverSocket.listen(5) #Listens for Client Connection
print('The ClassChat Server is ready.') #Print Message/Acknowledgement while waiting for client

clients = [] #List to keep track of connected clients
thread = [] #List to keep track of client thread

while True:
    connectionSocket, addr = serverSocket.accept() #Accepts Connection from Client
    clients.append(connectionSocket) #Adds Client Socket to List of Connected Clients
    newthread = threading.Thread(target=handle_client, args=(connectionSocket,)) #Create thread to handle client communication
    newthread.start() #Start the thread
    thread.append(newthread)
    
    username = connectionSocket.recv(1024).decode() #Receives Welcome Message from Client
    print(f"Received from client {addr}: {username}") #Prints Welcome Message from Client
    broadcast_message(f"Client {username} has joined the chat.", connectionSocket) #Broadcasts message to all clients that a new client has joined the chat
    connectionSocket.send("ACK: Connection Established.".encode()) #Sends Acknowledgement Message to Client    

    # Loop to handle multiple messages from the same client
    while True: 
        data = connectionSocket.recv(1024) #Receives Message from Client
        if not data:   #If no data is received, the client has disconnected
            print("Client disconnected.") #Print message indicating client disconnection
            clients.remove(connectionSocket) #Remove client from list of connected clients
            thread.remove(newthread) #Remove thread from list of client thread
            connectionSocket.close() #Close the client socket
            break #Exit loop to close connection and wait for new clients
        
        message = data.decode() #Decode message from client
        print(f"Received from client {addr}: {message}") #Print message received from client
        broadcast_message(f"Client {username} has sent a message.", connectionSocket) #Broadcasts message to all clients that a new client has sent a message
        connectionSocket.send(message.upper().encode()) #Sends back the message in uppercase to the client as a response

    connectionSocket.close()