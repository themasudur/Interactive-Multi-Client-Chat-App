import socket
import select
import sys
import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog

HOST = '127.0.0.1'
PORT = 5555

class Client(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        self.group_chat_button.clicked.connect(self.start_group_chat)

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
        while True:
            try:
                # I/O multiplexing using select() method
                read_sockets, _, _ = select.select([self.client_socket], [], [], 0.1)
                if self.client_socket in read_sockets:
                    message = self.client_socket.recv(1024).decode()
                    if message:
                        self.chat_area.setTextColor(QtGui.QColor("black"))
                        self.chat_area.append(message)
                    else:
                        self.chat_area.append("Disconnected from server.")
                        self.client_socket.close()
                        break
            except Exception as e:
                self.chat_area.append(f"Error: {e}")
                break

    def send_message(self):
        message = self.message_entry.text()
        if message:
            try:
                self.client_socket.sendall(message.encode())
                # Display sent message in blue
                self.chat_area.setTextColor(QtGui.QColor("blue"))
                self.chat_area.append(f"You: {message}")
                self.message_entry.clear()
            except Exception as e:
                self.chat_area.append(f"Error sending message: {e}")


    def start_group_chat(self):
        QtWidgets.QMessageBox.information(self, "Group Chat", "Starting group chat...")

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
        file_dialog = QFileDialog(self)
        save_path, _ = file_dialog.getSaveFileName(self, "Save File", file_name)
    
        if save_path:
            try:
                with open(save_path, "wb") as file:
                    file.write(file_data)
                self.chat_area.append(f"[Server] File {file_name} received from {sender_name}.")
            except Exception as e:
                self.chat_area.append(f"[Error] Failed to save file: {e}")
      
 
  
 
    def closeEvent(self, event):
        # Close the socket when the window is closed
        if self.client_socket:
            self.client_socket.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    client = Client()
    sys.exit(app.exec_())
