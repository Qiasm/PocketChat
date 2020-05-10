# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QSizePolicy, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QMessageBox
from PyQt5.QtWidgets import QDockWidget, QPushButton, QAction, QStyleFactory, QTextBrowser
import socket
import errno

from sys import exit as sys_exit

HEADER_LENGTH = 200

ip_file = open('server_ip.txt', 'r')

ip_address = str(ip_file.readlines(1))
IP = ip_address[2:-2].strip()
PORT = 5005

full_username = ""
clear_username = ""
curr_users = ""

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


def close_app():
    client_socket.close()
    sys_exit(0)


# Status Bar Handler
def set_status_bar(parent):
    status_msg = ''
    parent.StatBar = parent.statusBar()

    if len(status_msg) < 1:
        status_msg = 'Ready'

    parent.StatBar.showMessage(status_msg)


class MenuToolBar(QDockWidget):
    def __init__(self, parent):
        QDockWidget.__init__(self)
        self.Parent = parent
        self.Parent = parent.menuBar()
        # ******* Setup the Dictionary for the Tool Bar or other kind of reference
        self.MenuActRef = {'FileAct': 0,
                           'ExitAct': 0}
        # ******* Create the File Menu *******
        self.FileMenu = self.Parent.addMenu('File')
        # ******* Create Exit Menu Items *******
        self.ExitAct = QAction('Quit', self)
        self.ExitAct.setShortcut("Ctrl+Q")
        self.ExitAct.setStatusTip('Close the app.')
        self.ExitAct.triggered.connect(close_app)
        self.MenuActRef['ExitAct'] = self.ExitAct
        # ******* Setup the File Menu *******
        self.FileMenu.addAction(self.ExitAct)


class CenterPanel(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.Parent = parent
        # -----
        self.chatWindow = QTextBrowser()
        self.chatWindow.setStyleSheet("font: 15pt \"MS Shell Dlg 2\";")
        self.chatInput = QLineEdit()
        self.chatInput.setStyleSheet("font: 13pt \"MS Shell Dlg 2\";")
        self.chatInput.returnPressed.connect(self.message_sender)
        self.chatInput.setMaxLength(270)
        self.chatInput.hide()
        self.usernameInput = QLineEdit()
        self.usernameInput.setStyleSheet("font: 17pt \"MS Shell Dlg 2\";")
        self.usernameInput.setAlignment(Qt.AlignCenter)
        self.usernameInput.setMaxLength(15)
        self.usernameInput.returnPressed.connect(self.user_setter)
        # -----
        self.sendButton = QPushButton()
        self.sendButton.setStatusTip("Send a message.")
        self.sendButton.setText('Send')
        self.sendButton.clicked.connect(self.message_sender)
        self.sendButton.setDisabled(True)
        # -----
        self.activeUsersLabel = QLabel()
        self.activeUsersLabel.setStyleSheet("font: 20pt \"MS Shell Dlg 2\";")
        self.activeUsersLabel.setText('Active users')
        # -----
        self.usersWindow = QTextBrowser()
        self.usersWindow.setStyleSheet("font: 20pt \"MS Shell Dlg 2\";")
        # -----
        self.setUserButton = QPushButton()
        self.setUserButton.setText("Set username")
        self.setUserButton.setStatusTip("Set your username.")
        self.setUserButton.setStyleSheet("font: 13pt \"MS Shell Dlg 2\";")
        self.setUserButton.clicked.connect(self.user_setter)
        # -----
        hbx_btn_left = QHBoxLayout()
        hbx_btn_left.addWidget(self.chatInput)
        hbx_btn_left.addWidget(self.sendButton)
        self.chatInput.setMaximumSize(500, 35)
        self.sendButton.setMinimumSize(1, 35)
        # -----
        vbx_left_side = QVBoxLayout()
        vbx_left_side.addWidget(self.chatWindow)
        vbx_left_side.addLayout(hbx_btn_left)
        # -----
        hbx_labl_rite = QHBoxLayout()
        hbx_labl_rite.addWidget(self.activeUsersLabel)
        hbx_labl_rite.addStretch(1)
        # -----
        hbx_btn_rite = QHBoxLayout()
        hbx_btn_rite.addStretch(1)
        hbx_btn_rite.addWidget(self.setUserButton)
        self.setUserButton.setMinimumSize(120, 40)
        hbx_btn_rite.addStretch(1)
        # -----
        vbx_rite_side = QVBoxLayout()
        vbx_rite_side.addLayout(hbx_labl_rite)
        vbx_rite_side.addWidget(self.usersWindow)
        vbx_rite_side.addWidget(self.usernameInput)
        self.usernameInput.setMinimumSize(100, 50)
        vbx_rite_side.addLayout(hbx_btn_rite)
        # -----
        hbx_all = QHBoxLayout()
        hbx_all.addLayout(vbx_left_side)
        hbx_all.addLayout(vbx_rite_side)

        self.setLayout(hbx_all)

    def message_sender(self):
        self.chatInput.setFocus()
        check_input = self.chatInput.text()
        if check_input != "" and check_input != " ":
            print('(DEBUG) SENDING THE MESSAGE...')
            msg = self.chatInput.text()
            if len(msg) > 0:
                self.Parent.send_message(msg)

    def user_setter(self):
        check_user_input = self.usernameInput.text()
        if check_user_input != "" and check_user_input != " " and not check_user_input.isspace():
            print('(DEBUG) SETTING THE USERNAME...')
            self.User = self.usernameInput.text()
            self.Parent.set_username(self.User)


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle('Pocket Chat')

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(QSizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)

        chat_icon = QIcon()
        chat_icon.addPixmap(QPixmap("logo.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(chat_icon)

        self.CenterPanel = CenterPanel(self)
        self.setCentralWidget(self.CenterPanel)

        self.MenuToolBar = MenuToolBar(self)

        set_status_bar(self)
        self.setStyle(QStyleFactory.create('Cleanlooks'))

    def closeEvent(self, event):
        global full_username
        global clear_username
        reply = QMessageBox.question(
            self, "Message", "Are you sure you want to quit?", QMessageBox.Close | QMessageBox.Cancel
        )

        if reply == QMessageBox.Close and self.CenterPanel.usernameInput.isEnabled():
            username = str(clear_username).strip()
            data = "!UnSaEmRe@" + username
            self.send_message(data)
            event.accept()
        elif reply == QMessageBox.Close and not self.CenterPanel.usernameInput.isEnabled():
            event.accept()
        else:
            event.ignore()

    def send_message(self, msg):
        message = msg.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        print('(DEBUG) MESSAGE MSG: ' + str(message))
        print('(DEBUG) MESSAGE HEADER MSG: ' + str(message_header))
        full_message = message_header + message
        print('(DEBUG) FULL MSG BEING SENT: ' + str(full_message))
        self.CenterPanel.chatInput.setText("")
        self.CenterPanel.chatInput.setFocus()

        client_socket.send(full_message)

    def set_username(self, username):
        global clear_username
        global full_username
        clear_username = (16 - len(username)) * " " + username
        username = clear_username.encode('utf-8')
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        full_username = username_header + username
        print('(DEBUG) FULL USERNAME BEING SENT: ' + str(full_username))
        client_socket.send(full_username)
        self.CenterPanel.chatInput.show()

        self.CenterPanel.setUserButton.hide()
        self.CenterPanel.usernameInput.hide()
        self.CenterPanel.sendButton.setDisabled(False)

        self.start_thread()

    def start_thread(self):
        self.thread = ReceiverThread()
        self.thread.data_received.connect(self.on_receive_data)
        self.thread.user_data_received.connect(self.get_new_user)

        self.thread_holder = QThread()
        self.thread.moveToThread(self.thread_holder)  # NON-SUB-CLASSING QThread
        self.thread_holder.started.connect(self.thread.thread_runner)

        self.thread_holder.start()

    def on_receive_data(self, full_msg):
        sb = self.CenterPanel.chatWindow.verticalScrollBar()
        sb_val = float(sb.value())
        sb_max = float(sb.maximum())

        if self.CenterPanel.chatWindow.toPlainText() != "":
            current_chat = self.CenterPanel.chatWindow.toPlainText()
            self.CenterPanel.chatWindow.setText((current_chat + "\n" + f"{full_msg}"))
        else:
            self.CenterPanel.chatWindow.setText(f"{full_msg}")

        if sb_max == sb_val:
            sb.setValue(sb.maximum())
        else:
            sb.setValue(int(sb_val))

    def get_new_user(self, data):
        global clear_username
        global curr_users

        print("(DEBUG) get_new_user() FUNC DATA: " + data)

        curr_users = ""
        users_win = self.CenterPanel.usersWindow
        users_win.setText("")

        data = data[1:]
        data = data.lstrip()

        data_list = data.split("|-|")
        del data_list[-1]

        for i in range(1, len(data_list)):
            if len(data_list) >= 2:
                data_list[i] = data_list[i][11:]
                data_list[i] = data_list[i].lstrip()

        print(data_list)

        for user in data_list:
            if user == clear_username.strip():
                users_win.setText(curr_users + "◆ " + user + " (You)\n")
            else:
                users_win.setText(curr_users + "◆ " + user + "\n")
            curr_users = users_win.toPlainText()


class ReceiverThread(QObject):  # NON-SUB-CLASSING QThread
    data_received = pyqtSignal(object)
    user_data_received = pyqtSignal(object)

    def __init__(self):
        QObject.__init__(self)
        self.center_panel = CenterPanel(self)

    def thread_runner(self):
        print("\n (DEBUG) RECEIVER THREAD STARTED \n")
        while True:
            try:
                while True:
                    # receive things
                    username_header = client_socket.recv(HEADER_LENGTH)
                    user_joined = username_header.decode('utf-8')
                    print(f"(DEBUG) USERNAME HEADER: {user_joined}")
                    if "!UnSaEmRe@" in user_joined[:10]:
                        print("(DEBUG) SOMEONE JOINED/STR USERNAME DATA: " + str(user_joined))
                        clear_data = str(user_joined)[10:]
                        print("(DEBUG) CLEARED USER DATA: " + clear_data)
                        self.user_data_received.emit(str(clear_data).replace("'", ""))
                        raise BreakLoop
                    else:
                        print("(DEBUG) RECEIVED DATA FROM THE SERVER")
                        if not len(username_header):
                            print("(DEBUG) Connection closed by the server.")
                            sys_exit()

                        username_length = int(username_header.decode('utf-8'))
                        username = client_socket.recv(username_length).decode('utf-8')

                        message_header = client_socket.recv(HEADER_LENGTH)
                        message_length = int(message_header.decode('utf-8'))
                        message = client_socket.recv(message_length).decode('utf-8')

                        full_message = str(username).lstrip() + ": " + str(message).strip()
                        print(f"(DEBUG) | {username.lstrip()}: {message}")

                        self.data_received.emit(full_message)

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print("Reading error", str(e))
                    sys_exit()
                continue

            except BreakLoop:
                pass

            except Exception as e:
                print("General error", str(e))
                sys_exit()


class BreakLoop(Exception):
    pass


if __name__ == "__main__":
    MainThread = QApplication([])

    MainWindow = Window()
    MainWindow.show()

    sys_exit(MainThread.exec_())
