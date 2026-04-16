from socket import socket, AF_INET, SOCK_STREAM
import select

serverName = 'localhost' #Server Name
serverPort = 12000 #Port Number
clientSocket = socket(AF_INET, SOCK_STREAM) #TCP Client Socket
clientSocket.connect((serverName,serverPort)) #Socket Connection

username = input('Input your Username:') #User/Client Input
ready = select.select([clientSocket], [], [], 5) #Wait for Server Response
clientSocket.send(username.encode()) #Send input to server
clientUsername = clientSocket.recv(1024) #Wait for and receive server response
print('From ClassChat Server: ', clientUsername.decode()) #print server response

clientSocket.close() #Close Client Socket