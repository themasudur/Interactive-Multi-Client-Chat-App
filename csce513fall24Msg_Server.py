import socket
import select
import sys
import threading
from PyQt5 import QtWidgets, QtCore, QtGui

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# Define a shared key (must be 32 bytes for AES-256)
SHARED_KEY = b"thisisaverysecurekey123456789012"  # Example 32-byte key (do not share this publicly)
IV = b"1234567890123456"  # Initialization vector (must be 16 bytes)

HOST = '127.0.0.1'
PORT = 5555

clients = {}
client_status = {}
offline_messages = {}
groups = {}

class Server(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.init_ui()
<<<<<<< HEAD
=======
        

>>>>>>> 7175864c62c067fa11f6df0b8b5724f68c74c233
        self.start_server()

    def init_ui(self):
        self.setWindowTitle("csce513fall2024Msg Server")
        self.setGeometry(100, 100, 400, 400)

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.CustomizeWindowHint)

        self.setWindowIcon(QtGui.QIcon("icons/server.png"))
        
        self.chat_area = QtWidgets.QTextEdit(self)
        self.chat_area.setReadOnly(True)
        
        self.client_list = QtWidgets.QListWidget(self)
        
        chat_label = QtWidgets.QLabel("Chat History")        
        client_label = QtWidgets.QLabel()
        icon = QtGui.QPixmap("icons/client.png")
        client_label.setPixmap(icon)
        client_label.setText(" Online Clients")
        
        main_layout = QtWidgets.QVBoxLayout()
        content_layout = QtWidgets.QHBoxLayout()
        chat_layout = QtWidgets.QVBoxLayout()
        chat_layout.addWidget(chat_label)
        chat_layout.addWidget(self.chat_area)
        client_layout = QtWidgets.QVBoxLayout()
        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_list)
        content_layout.addLayout(chat_layout, 3)
        content_layout.addLayout(client_layout, 2)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        self.show()

    def start_server(self):
        try:
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            threading.Thread(target=self.run_server, daemon=True).start()
        except socket.error as e:
            self.chat_area.setTextColor(QtGui.QColor("red"))
            self.chat_area.append(f"Socket error: {e}")

    def run_server(self):
        sockets = [self.server_socket]
        while True:
            try:
                read_sockets, _, _ = select.select(sockets, [], [])
                for s in read_sockets:
                    if s == self.server_socket:
                        client_socket, client_address = self.server_socket.accept()
                        sockets.append(client_socket)
                        self.handle_client(client_socket)
                    else:
                        try:
                            message = s.recv(1024)
                            decrypted_message = self.decrypt_message(message)
                            
                            #print(decrypted_message)
                            if decrypted_message:
                                self.process_client_message(s, decrypted_message)
                        except OSError:
                            self.remove_client(s, sockets)
            except (OSError, ValueError):
                break

    def handle_client(self, client_socket):
        try:
            client_name = client_socket.recv(1024).decode()
            clients[client_socket] = client_name
            client_status[client_name] = "Active"
            self.update_client_list()
            self.chat_area.setTextColor(QtGui.QColor("blue"))
            self.chat_area.append(f"{client_name} has joined the chat")

            if client_name in offline_messages:
                for message in offline_messages[client_name]:
                    client_socket.sendall(message.encode())
                del offline_messages[client_name]
        except:
            pass

    def process_client_message(self, client_socket, message):
        """Decrypt and process a message sent by a client."""
        
        sender_name = clients.get(client_socket, "Unknown")
        
        #print(message)
        
        # Handle file transfer request
        if message.startswith("[FileTransfer]"):
            try:
                _, recipient_name, file_name, data = message.split(":")
                self.handle_file_transfer_request(sender_name, recipient_name.strip(), file_name.strip(), data.strip())
            except ValueError:
                client_socket.sendall("[Error] Invalid file transfer format.".encode())
        
        
        # Handle direct messages
        elif message.startswith("@"):
            try:
                recipient_name, msg = message[1:].split(" ", 1)
                self.send_to_recipient(sender_name, recipient_name.strip(), msg.strip())
            except ValueError:
                client_socket.sendall("[Error] Invalid message format. Use @recipient message".encode())
    
    
        elif message.startswith("[GroupNotification]"):
            _, group_name, member_name = message.split(":")
            self.handle_group_notification(group_name.strip(), member_name.strip(), client_socket)
  
        elif message.startswith("&"):
            try:
                group_name, msg = message[1:].split(" ", 1)
                self.broadcast_group_message(group_name.strip(), sender_name, msg.strip())
            except ValueError:
                client_socket.sendall("[Error] Invalid group message format.".encode())
<<<<<<< HEAD
            return
          
        #print(len(message))
        self.broadcast_message(client_socket, message)

=======
        # Handle broadcast messages
        else:
            #print(len(message))
            self.broadcast_message(client_socket, message)
>>>>>>> 7175864c62c067fa11f6df0b8b5724f68c74c233

    def send_to_recipient(self, sender_name, recipient_name, msg):
        """Send message to a specific recipient or notify sender if offline."""
        #print("Sender: ",sender_name)
        #print("Recipent: ",recipient_name)
        #print("Msg: ",msg)
        #print("All clients: ", list(clients.values()))
        if recipient_name in list(clients.values()) and client_status[recipient_name] == "Active":
            #print("OK, I got you")
            recipient_socket = [sock for sock, name in clients.items() if name == recipient_name][0]
            recipient_socket.sendall(f"[{sender_name}]: {msg}".encode())
            self.chat_area.setTextColor(QtGui.QColor("black"))
            self.chat_area.append(f"[{sender_name} to {recipient_name}]: {msg}")
        else:
            self.store_offline_message(recipient_name, f"[{sender_name}]: {msg}")
            self.chat_area.setTextColor(QtGui.QColor("blue"))
            self.chat_area.append(f"[Server] {recipient_name} is not online. Message stored.")

            sender_socket = [sock for sock, name in clients.items() if name == sender_name][0]
            sender_socket.sendall(
                f"[Server] User {recipient_name} is not online. Message stored. "
                "They will receive it when they are available.".encode()
            )

    def store_offline_message(self, recipient_name, msg):
        if recipient_name not in offline_messages:
            offline_messages[recipient_name] = []
        offline_messages[recipient_name].append(msg)

    def broadcast_message(self, client_socket, message):
        """Broadcast an encrypted message to all clients."""

        sender_name = clients.get(client_socket, "Unknown")
        self.chat_area.setTextColor(QtGui.QColor("black"))
        self.chat_area.append(f"[{sender_name} to All]: {message}")
        
        # Encrypt the message
        encrypted_message = self.encrypt_message(message)
        
        
        for client in clients:
            if client != client_socket:
                try:
<<<<<<< HEAD
                    client.sendall(f"[{sender_name}] ".encode() + encrypted_message)
                except OSError:
                    self.remove_client(client)
                
                self.remove_client(client)
                    
=======
                    client.sendall(f"[{sender_name}]: {encrypted_message}")
                except OSError:
                    self.remove_client(client)




>>>>>>> 7175864c62c067fa11f6df0b8b5724f68c74c233
    def remove_client(self, client_socket, sockets):
        client_name = clients.pop(client_socket, None)
        if client_name:
            client_status[client_name] = "Inactive"
            sockets.remove(client_socket)
            client_socket.close()
            self.update_client_list()
            self.chat_area.setTextColor(QtGui.QColor("blue"))
            self.chat_area.append(f"{client_name} has left the chat")

    def update_client_list(self):
        self.client_list.clear()
        for client_name, status in client_status.items():
            self.client_list.addItem(f"{client_name} ({status})")


    # Add these methods to the Server class
    
    def handle_file_transfer_request(self, sender_socket, recipient_name, file_name, data):
        """Handle file transfer."""
        sender_name = clients.get(sender_socket, "Unknown")
    
        if recipient_name in list(clients.values()) and client_status[recipient_name] == "Active":
            recipient_socket = [sock for sock, name in clients.items() if name == recipient_name][0]
            
            recipient_socket.sendall(
                f"[FileTransferRequest]:{sender_name}:{file_name}:{data}".encode()
            )
            self.chat_area.setTextColor(QtGui.QColor("blue"))
            self.chat_area.append(f"[Server] File transfer request from {sender_name} to {recipient_name}.")
        else:
            sender_socket.sendall(
                f"[Server] User {recipient_name} is not online. File transfer request failed.".encode()
            )
    

    def handle_group_notification(self, group_name, member_name, client_socket):
        """Add a member to a group and notify other members."""
        if group_name not in groups:
            groups[group_name] = {"members": set(), "sockets": set()}
    
        groups[group_name]["members"].add(member_name)
        groups[group_name]["sockets"].add(client_socket)
    
        # Notify all group members about the new member
        for socketed in groups[group_name]["sockets"]:
            try:
                socketed.sendall(
                    f"[GroupNotification]:{group_name}:{member_name}".encode()
                )
            except OSError:
                self.remove_client(socketed)
    
        self.chat_area.append(f"[Server] {member_name} added to group {group_name}.")
    
    
    def broadcast_group_message(self, group_name, sender_name, message):
        """Send a message to all members of the group."""
        print(group_name, sender_name, message)
        if group_name in groups:
            for client_socket in groups[group_name]["sockets"]:
                print("\n\n")
                print(client_socket)
                try:
                    # Encrypt and send the message
                    full_message = f"&{group_name}:{sender_name}: {message}"
                    encrypted_message = self.encrypt_message(full_message)
                    client_socket.sendall(encrypted_message)

                except OSError:
                    self.remove_client(client_socket)
    
            self.chat_area.append(f"[{sender_name} to Group {group_name}]: {message}")
        else:
            sender_socket = [sock for sock, name in self.clients.items() if name == sender_name][0]
            sender_socket.sendall(f"[Server] Group {group_name} does not exist.".encode())
            



    def send_file_to_recipient(self, recipient_socket, file_data, file_name, sender_name):
        """Send file data to the recipient."""
        try:
            recipient_socket.sendall(f"[FileTransfer]:{file_name}:{sender_name}".encode())
            recipient_socket.sendall(file_data)
            self.chat_area.append(f"[Server] File {file_name} sent from {sender_name}.")
        except Exception as e:
            self.chat_area.append(f"[Error] File transfer failed: {e}")

    def encrypt_message(self, message):
         """Encrypt a message using AES."""
         # Pad the message to match block size
         padder = padding.PKCS7(128).padder()
         padded_data = padder.update(message.encode()) + padder.finalize()
     
         # Encrypt the padded message
         cipher = Cipher(algorithms.AES(SHARED_KEY), modes.CBC(IV))
         encryptor = cipher.encryptor()
         encrypted_message = encryptor.update(padded_data) + encryptor.finalize()
         return encrypted_message
<<<<<<< HEAD
=======
     
>>>>>>> 7175864c62c067fa11f6df0b8b5724f68c74c233
        
    def decrypt_message(self, encrypted_message):
         """Decrypt a message using AES."""
         # Decrypt the message
         cipher = Cipher(algorithms.AES(SHARED_KEY), modes.CBC(IV))
         decryptor = cipher.decryptor()
         decrypted_data = decryptor.update(encrypted_message) + decryptor.finalize()
         
         # Remove padding
         unpadder = padding.PKCS7(128).unpadder()
         decrypted_message = unpadder.update(decrypted_data) + unpadder.finalize()
         return decrypted_message.decode()
<<<<<<< HEAD
=======

    



>>>>>>> 7175864c62c067fa11f6df0b8b5724f68c74c233

    def closeEvent(self, event):
        if self.server_socket:
            self.server_socket.close()
        event.accept()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    server = Server()
    sys.exit(app.exec_())
