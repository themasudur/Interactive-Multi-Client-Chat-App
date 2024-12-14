## Interactive Multi-client Chat System using Socket in Python

## Problem Statement:

Design and develop an online chat system, named csce513fall24Msg, for communications and discussions among students in a class. The csce513fall24Msg is expected to enable the students to chat with the instructor and their classmates for any necessary discussion, e.g., homework problem.

## csce513fall24Msg

`csce513fall24Msg` is a online chat application designed for students to communicate and discuss with the instructor and their classmates for any necessary discussion, e.g., homework problem.

## Table of Contents

- [Features](#features)
- [Functionality](#functionality)
- [Technologies](#technologies)
- [Run](#run)

## Features

1. **Basic Client-Server Communication using TCP/IP**: Communication with each other through socket programming using TCP/IP. The communication between two clients will go through the server.
2. **Advanced Client using I/O multiplexing**: A client can send and receive messages at the same time with less CPU workload using I/O multiplexing.
3. **Multi-Thread Communication Server**: Multiple students can discuss class topics or homework problems at the same time.
4. **Client-Client Communication**: Clients communicate with each other by passing messages through the server.
5. **Group chat**: Each group member can send and receive messages in the group chat window. These messages are visible to all group members.
6. **File transfer**: A client can transfer a file to another client by using csce513fall24Msg.
7. **Offline message**: The server can save the message for offline clients (not connecting to the server). Once these clients get connected to the server, the stored message can be forwarded to them.
8. **Secure communication**: Encryption & decryption in the transmitted messages using the public and private key to generate and transmit session key.

## Functionality

The `csce513fall24Msg` system operates on a client-server architecture, where all client communications are routed through the server. The application supports concurrent users.

- **Server**: Handles incoming connections, message routing, and client management. Uses multi-threading to support multiple users.
- **Client**: Each client connects to the server and enables real-time chat in a graphical environment.
- **Encryption**: RSA-based secure message exchange ensures security.

## Technologies

- **Socket Programming**: Enables TCP-based communication for real-time messaging.
- **Threading**: Each client connection runs in its own thread for concurrent handling. multiple concurrent users
- **Encryption**: Implements RSA for secure message exchanges.
- **GUI (PyQt5)**: Displays client lists, group memberships, and chat messages.

## Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/csce513fall24Msg.git
   cd csce513fall24Msg

2. **Run the server**:
   ```bash
   $python csce513fall24Msg_Server.py
   
3. **Run the Client**
   ```bash
   $python csce513fall24Msg_Client.py
A prompt will ask for `username` when user wants to join the chatroom and accepts the connection only if the username is unique.

## About 
This is designed and written by `Masud.`
