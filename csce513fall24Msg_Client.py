from PyQt5 import QtWidgets, QtGui, QtCore
import socket
import threading
import select
import sys
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# Define a shared key (must be 32 bytes for AES-256)
<<<<<<< HEAD
SHARED_KEY = b"thisisaverysecurekey123456789012"  # Example 32-byte key
=======
SHARED_KEY = b"thisisaverysecurekey123456789012"  # Example 32-byte key (do not share this publicly)
>>>>>>> 7175864c62c067fa11f6df0b8b5724f68c74c233
IV = b"1234567890123456"  # Initialization vector (must be 16 bytes)



HOST = '127.0.0.1'
PORT = 5555


class GroupChatWindow(QtWidgets.QWidget):
    """Group Chat Management Window with Chat Display"""
    def __init__(self, client_socket, group_name):
        super().__init__()

        self.client_socket = client_socket
        self.group_name = group_name
        self.members = set()

        self.init_ui()

    def init_ui(self):
        """Initialize UI for Group Chat Window."""
        
        self.setWindowTitle(f"Group name: {self.group_name}")
        self.setGeometry(100, 100, 300, 400)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.CustomizeWindowHint)
        self.setWindowIcon(QtGui.QIcon("icons/group.png"))
        
        # Create widgets
        self.member_input = QtWidgets.QLineEdit(self)
        self.member_input.setPlaceholderText("Enter member name...")
        
        self.add_member_button = QtWidgets.QPushButton("Add Member", self)
        self.add_member_button.setMaximumWidth(120)  # Adjust button width
        self.add_member_button.clicked.connect(self.add_member)
        
        self.member_list_label = QtWidgets.QLabel("Group Members")
        self.member_list = QtWidgets.QListWidget(self)
        
        
        self.chat_label = QtWidgets.QLabel("Group Conversation")
        self.group_chat_area = QtWidgets.QTextEdit(self)
        self.group_chat_area.setReadOnly(True)
        
        # Create layouts
        main_layout = QtWidgets.QVBoxLayout()
        
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.member_input, 2)
        input_layout.addWidget(self.add_member_button, 1)
        main_layout.addLayout(input_layout)
        
        
        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addWidget(self.member_list_label, 1)
        label_layout.addWidget(self.chat_label, 2)
        main_layout.addLayout(label_layout)
        
        list_layout = QtWidgets.QHBoxLayout()
        list_layout.addWidget(self.member_list, 1)
        list_layout.addWidget(self.group_chat_area, 2)
        main_layout.addLayout(list_layout)
        
        self.setLayout(main_layout)

    def add_member(self):
        """Add a new member to the group."""
        member_name = self.member_input.text().strip()
        if member_name and member_name not in self.members:
            self.members.add(member_name)
            self.member_list.addItem(member_name)

            # Notify the server about the new member
            self.client_socket.sendall(
                f"[GroupNotification]:{self.group_name}:{member_name}".encode()
            )

            QtWidgets.QMessageBox.information(
                self, "Group Notification", f"{member_name} added to {self.group_name}"
            )
            self.member_input.clear()
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", "Invalid or duplicate member name."
            )

    def display_group_message(self, message, color="purple"):
        """Display a message in the group chat area."""
        self.group_chat_area.setTextColor(QtGui.QColor(color))
        self.group_chat_area.append(message)


class Client(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.group_windows = {}
        self.init_ui()
        self.connect_to_server()
        
        
        
  
        

    def init_ui(self):
        self.setWindowTitle("csce513fall2024Msg Client")
        self.setGeometry(100, 100, 300, 400)

        # Remove minimize and maximize buttons
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.CustomizeWindowHint)

        # Set window icon
        self.setWindowIcon(QtGui.QIcon("icons/client.png"))  # Replace with your client icon file path

        # Prompt for the username
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint
        self.name, ok = QtWidgets.QInputDialog.getText(
            self, 
            "Welcome", 
            "Enter your name:", 
            flags=flags
        )
        
        if not ok or not self.name:
            sys.exit()
            
        # Create widgets
        self.name_label = QtWidgets.QLabel(f"Name: {self.name}")
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.name_label.setFont(bold_font)

        self.chat_area = QtWidgets.QTextEdit(self)
        self.chat_area.setReadOnly(True)

        self.message_entry = QtWidgets.QLineEdit(self)
        self.message_entry.setPlaceholderText("Enter your message...")
        self.message_entry.returnPressed.connect(self.send_message)  # Send message on Enter key press

        # Create send button with icon
        self.send_button = QtWidgets.QPushButton(" Send")
        self.send_button.setIcon(QtGui.QIcon("icons/send.png"))  # Replace with your send icon file path
        self.send_button.clicked.connect(self.send_message)

        # Create action buttons with icons
        self.group_chat_button = QtWidgets.QPushButton(" Group Chat")
        self.group_chat_button.setIcon(QtGui.QIcon("icons/group.png"))  # Replace with your group chat icon file path
        self.group_chat_button.clicked.connect(self.open_group_chat)

        self.send_file_button = QtWidgets.QPushButton(" Send a File")
        self.send_file_button.setIcon(QtGui.QIcon("icons/file.png"))  # Replace with your send file icon file path
        self.send_file_button.clicked.connect(self.send_file)

        # Create layouts
        main_layout = QtWidgets.QVBoxLayout()
        message_layout = QtWidgets.QHBoxLayout()
        action_layout = QtWidgets.QHBoxLayout()

        # Arrange widgets
        message_layout.addWidget(self.message_entry)
        message_layout.addWidget(self.send_button)

        action_layout.addWidget(self.group_chat_button)
        action_layout.addWidget(self.send_file_button)

        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.chat_area)
        main_layout.addLayout(message_layout)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

        self.show()


    def connect_to_server(self):
        try:
            self.client_socket.connect((HOST, PORT))
            self.client_socket.sendall(self.name.encode())
            # client thread
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Connection Error", f"Could not connect to server: {e}")
            sys.exit()

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


    def receive_messages(self):
        """Receive and decrypt messages from the server."""
        while True:
            try:
                read_sockets, _, _ = select.select([self.client_socket], [], [], 0.1)
                if self.client_socket in read_sockets:
<<<<<<< HEAD
                    message = self.client_socket.recv(1024)
                    
                    if message:
                        # Split the sender name and encrypted message
                        sender_end_idx = message.find(b"] ") + 2  # Find the end of the sender name
                        sender_name = message[:sender_end_idx].decode()  # Extract sender name (e.g., "[Sender] ")
                        encrypted_message = message[sender_end_idx:]  # Extract encrypted content
        
                        # Decrypt the encrypted part
                        decrypted_message = self.decrypt_message(encrypted_message)

                        # Handle group messages
                        if decrypted_message.startswith("&"):
                            group_name, sender_name, group_msg = decrypted_message[1:].split(" ", 2)
                            if group_name in self.group_windows:
                                self.group_windows[group_name].display_group_message(f"[{sender_name}]: {group_msg}", "purple")
                                self.chat_area.setTextColor(QtGui.QColor("purple"))
                                self.chat_area.append(f"[{group_name}]: {group_msg}")
                            else:
                                # Display in main chat if group is not open
                                self.chat_area.setTextColor(QtGui.QColor("purple"))
                                self.chat_area.append(f"[{group_name}]: {group_msg}")
    
                        elif decrypted_message.startswith("@"):
                            print(decrypted_message)
                            receipent_name, msg = decrypted_message.split(" ")
                            self.chat_area.setTextColor(QtGui.QColor("green"))
                            self.chat_area.append(f"[sender_name] to {receipent_name}]: {msg}.")
                        
                        elif decrypted_message.startswith("[GroupNotification]"):
                            _, group_name, member_name = decrypted_message.split(":")
                            self.chat_area.setTextColor(QtGui.QColor("green"))
                            self.chat_area.append(f"[Server] {member_name} was added to group {group_name}.")
    
                        else:
                            self.chat_area.setTextColor(QtGui.QColor("black"))
                            self.chat_area.append(f"{sender_name}: {decrypted_message}")
=======
                    encrypted_message = self.client_socket.recv(1024).decode()
                    
                    if encrypted_message:
                        # Decrypt the message
                        decrypted_message = self.decrypt_message(encrypted_message)

                    # Handle group messages
                    if decrypted_message.startswith("&"):
                        group_name, group_msg = decrypted_message[1:].split(":", 1)

                        if group_name in self.group_windows:
                            self.group_windows[group_name].display_group_message(group_msg)
                        else:
                            # Display in main chat if group is not open
                            self.chat_area.setTextColor(QtGui.QColor("purple"))
                            self.chat_area.append(f"[{group_name}]: {group_msg}")

                    # Handle notifications
                    elif decrypted_message.startswith("[GroupNotification]"):
                        _, group_name, member_name = decrypted_message.split(":")
                        self.chat_area.setTextColor(QtGui.QColor("green"))
                        self.chat_area.append(f"[Server] {member_name} was added to group {group_name}.")

                    else:
                        self.chat_area.setTextColor(QtGui.QColor("black"))
                        self.chat_area.append(decrypted_message)
>>>>>>> 7175864c62c067fa11f6df0b8b5724f68c74c233
            except Exception as e:
                self.chat_area.append(f"Error: {e}")
                break





    def send_message(self):
        """Send an encrypted message to the server."""
        message = self.message_entry.text().strip()
        if not message:
            return
        

        try:
            # Encrypt the message
            encrypted_message = self.encrypt_message(message)
            
            #print(encrypted_message)
            #print(self.decrypt_message(encrypted_message))
            
            
            self.client_socket.sendall(encrypted_message)

            if message.startswith("&"):
                self.chat_area.setTextColor(QtGui.QColor("purple"))
                self.chat_area.append(f"[Me]: {message}")
            else:
                self.chat_area.setTextColor(QtGui.QColor("blue"))
                self.chat_area.append(f"You: {message}")
            self.message_entry.clear()
        except Exception as e:
            self.chat_area.append(f"Error sending message: {e}")






    def send_file(self):
        """Send a file to another client."""
        recipient, ok = QtWidgets.QInputDialog.getText(self, "Send File", "Enter recipient's name:")
        if not ok or not recipient.strip():
            return
    
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select File to Send")
    
        if file_path:
            try:
                file_name = os.path.basename(file_path)    
                with open(file_path, "rb") as file:
                    data = file.read()
                self.client_socket.sendall(f"[FileTransfer]:{recipient}:{file_name}:{data}".encode())
                self.chat_area.append(f"[Me] Sent file {file_name} to {recipient}.")
    
            except Exception as e:
                self.chat_area.append(f"[Error] Could not send file: {e}")
    
    def receive_file(self, file_name, sender_name, file_data):
        """Receive a file sent from another client."""
        file_dialog = QtWidgets.QFileDialog(self)
        save_path, _ = file_dialog.getSaveFileName(self, "Save File", file_name)
    
        if save_path:
            try:
                with open(save_path, "wb") as file:
                    file.write(file_data)
                self.chat_area.append(f"[Server] File {file_name} received from {sender_name}.")
            except Exception as e:
                self.chat_area.append(f"[Error] Failed to save file: {e}")
      


    def open_group_chat(self):
        """Prompt for a group name before opening Group Chat Window."""
        group_name, ok = QtWidgets.QInputDialog.getText(self, "Group Name", "Enter a group name:")

        if ok and group_name.strip():
            if group_name not in self.group_windows:
                self.group_windows[group_name] = GroupChatWindow(self.client_socket, group_name.strip())
            self.group_windows[group_name].show()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid group name.")
 
    def closeEvent(self, event):
        # Close the socket when the window is closed
        if self.client_socket:
            self.client_socket.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    client = Client()
    sys.exit(app.exec_())