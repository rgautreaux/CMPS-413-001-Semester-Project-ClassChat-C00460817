# Semester Project Technical Report
## Introduction
The objective of this project is to design and develop an online chat system, named ClassChat, 
to be used for communications and discussions among students in a class. This Technical Report provides an overview of the design and implementation of the ClassChat system, including the architecture, technologies used, and challenges faced during development.

## System Design

ClassChat is designed to be a 

## 1 Client–Server Communication using TCP/IP
This section will describe the process of implementing the first step of this semester project: creating a client-server communication using TCP/IP. The server is intended to listen for incoming connections from clients, and clients will connect to the server to send and receive messages.

### 1.1 Server Implementation

Using the examples found in the textbook as a guide, I proceeded to create the `ClassChatClient.py` and `ClassChatServer.py` files for the server and client respectively. When inputing the code samples from the textbook, the VSCode editor automatically converted the single quotes to curly quotes, which caused syntax errors. I had to change the curly quotes back to straight quotes in order for the code to run properly.  I also changed the basic server name into "ClassChatServer" to make it more specific to this project.