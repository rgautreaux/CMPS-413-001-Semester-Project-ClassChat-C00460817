# Semester Project Technical Report
## Introduction
The objective of this project is to design and develop an online chat system, named ClassChat, 
to be used for communications and discussions among students in a class. This Technical Report provides an overview of the design and implementation of the ClassChat system, including the architecture, technologies used, and challenges faced during development.

## 1 Client–Server Communication using TCP/IP (30 points)

This section will describe the process of implementing the first step of this semester project: creating a client-server communication using TCP/IP. The server is intended to listen for incoming connections from clients, and clients will connect to the server to send and receive messages.

### 1.1 Server Implementation

Using the examples found in the textbook as a guide, I proceeded to create the `ClassChatClient.py` and `ClassChatServer.py` files for the server and client respectively. When inputting the code samples from the textbook chapter slides, the VSCode editor automatically identified syntax errors due to mismatched quotes, and I made the proper adjustments.  I also changed the basic server name into "ClassChatServer" to make it more specific to this project.

### 1.2 Client Implementation

When starting this step, I realized I had accidentally put the Client code into the Server file, and fixed this mistake. I then followed the same process for the client implementation, using the example in the textbook slides as a guide, and referring to it when writing the file contents.  Once both the Server and Client files were created, VSCode identified syntax errors in the code, specifically a Wildcard import error due to the `from socket import *` line from the textbook slide example at the top of both files. 

![alt text](/evidence-screenshots/import_problem.png)

The VSCode error flag provided the following link, which broke down the error and how to resolve it:
https://github.com/microsoft/pylance-release/blob/main/docs/diagnostics/reportWildcardImportFromLibrary.md

I used this guidance to change the import statement to `from socket import socket, AF_INET, SOCK_STREAM`, based on the `(server/client)Socket = socket(AF_INET,SOCK_STREAM)` calls later on in these files. This change resolved the syntax error and allowed me to proceed with the implementation of the client-server communication.

![alt text](/evidence-screenshots/import_error_fix.png)

### 1.3 Requirements  

The Client-Server pair are now created, with no remaining errors recognized by the VSCode editor. I adjusted the names of some variables to specifically fit the project, and not the template/example that I based the code on.Before proceeding into the next step of this project and implementing the Advanced Client requirements, I ran the server and client files to verify that their basic TCP/IP communication worked. 

![alt text](evidence-screenshots/ServerTest.png)
![alt text](evidence-screenshots/ClientTest_ERROR.png)

The Server launched and listened for clients as designed, but an error occurred when the Client attempted to connect.  I was unsure of the cause for this error, and asked Github Copilot for assistance in diagnosing the source of the issue. It stated that the reason for this problem was due to the `servername` variable not being a valid hostname or address, recommending I change it to `localhost`.  In hindsight, this was a very simple mistake that I should have caught myself, but I had been so focused on following the textbook example and getting the code to run that I overlooked this detail.

I did this and tried running the server and client again, and this time it worked. I was able to enter a username and receive a response from the server, confirming that the TCP/IP communication was successfully established between the client and server.

![alt text](evidence-screenshots/ClientTest_FIXED.png)

I thus added an entry to the `TRANSCRIPT.md` file to document the exact usage of Github Copilot to help identify this issue and find its resolution for full transparency.

## 2 Advanced Client (20 points)

Now that the simple client-server communication system has been created and verified, it was time to move onto the next step of Advancing Client capabilities so that a client can both send and receive message at the 
same time with less CPU workload. 

I/O multiplexing waws the suggested method of executing this task within the instructions, specifically to use system callback function to activate a client’s application if the socket receives data from the server or keyboard input from the user. Thus, I went back to the textbook chapter slides to review Multiplexing and how it worked.