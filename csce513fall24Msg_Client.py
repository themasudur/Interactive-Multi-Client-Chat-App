from PyQt5 import QtWidgets, QtGui, QtCore
import socket
import threading
import select
import sys
import os

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
        self.setWindowTitle(f"Group Chat - {self.group_name}")
        self.setGeometry(150, 150, 500, 400)

        # Chat area for group messages
        self.group_chat_area = QtWidgets.QTextEdit(self)
        self.group_chat_area.setReadOnly(True)

        # Member management
        self.member_input = QtWidgets.QLineEdit(self)
        self.member_input.setPlaceholderText("Enter member's name...")

        self.add_member_button = QtWidgets.QPushButton("Add Member", self)
        self.add_member_button.clicked.connect(self.add_member)

        self.member_list_label = QtWidgets.QLabel("Group Members:")
        self.member_list = QtWidgets.QListWidget(self)

        self.cancel_button = QtWidgets.QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.group_chat_area)
        layout.addWidget(self.member_input)
        layout.addWidget(self.add_member_button)
        layout.addWidget(self.member_list_label)
        layout.addWidget(self.member_list)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

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
        self.setWindowIcon(QtGui.QIcon("client_icon.png"))  # Replace with your client icon file path

        # Prompt for the username
        self.name, ok = QtWidgets.QInputDialog.getText(self, "Enter Name", "Enter your name:")
        if not ok or not self.name:
            sys.exit()
            
        # Create widgets
        self.name_label = QtWidgets.QLabel(f"Your Name: {self.name}")  # Replace with dynamic name if needed

        self.chat_area = QtWidgets.QTextEdit(self)
        self.chat_area.setReadOnly(True)

        self.message_entry = QtWidgets.QLineEdit(self)
        self.message_entry.setPlaceholderText("Enter your message...")
        self.message_entry.returnPressed.connect(self.send_message)  # Send message on Enter key press

        # Create send button with icon
        self.send_button = QtWidgets.QPushButton(self)
        self.send_button.setIcon(QtGui.QIcon("send.png"))  # Replace with your send icon file path
        self.send_button.clicked.connect(self.send_message)

        # Create action buttons with icons
        self.group_chat_button = QtWidgets.QPushButton(" Group Chat")
        self.group_chat_button.setIcon(QtGui.QIcon("group.png"))  # Replace with your group chat icon file path
        self.group_chat_button.clicked.connect(self.open_group_chat)

        self.send_file_button = QtWidgets.QPushButton(" Send a File")
        self.send_file_button.setIcon(QtGui.QIcon("file.png"))  # Replace with your send file icon file path
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



    def receive_messages(self):
        """Receive messages and handle them appropriately."""
        while True:
            try:
                read_sockets, _, _ = select.select([self.client_socket], [], [], 0.1)
                if self.client_socket in read_sockets:
                    message = self.client_socket.recv(1024).decode()

                    # Handle group messages
                    if message.startswith("&"):
                        group_name, group_msg = message[1:].split(":", 1)

                        if group_name in self.group_windows:
                            self.group_windows[group_name].display_group_message(group_msg)
                        else:
                            # Display in main chat if group is not open
                            self.chat_area.setTextColor(QtGui.QColor("purple"))
                            self.chat_area.append(f"[{group_name}]: {group_msg}")

                    # Handle notifications
                    elif message.startswith("[GroupNotification]"):
                        _, group_name, member_name = message.split(":")
                        self.chat_area.setTextColor(QtGui.QColor("green"))
                        self.chat_area.append(f"[Server] {member_name} was added to group {group_name}.")

                    else:
                        self.chat_area.setTextColor(QtGui.QColor("black"))
                        self.chat_area.append(message)
            except Exception as e:
                self.chat_area.append(f"Error: {e}")
                break

    def send_message(self):
        """Send a message to the server."""
        message = self.message_entry.text().strip()
        if message:
            try:
                self.client_socket.sendall(message.encode())

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
