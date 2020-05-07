import socket
import select

HEADER_LENGTH = 200

ip_file = open('server_ip.txt', 'r')

ip_adress = str(ip_file.readlines(1))
IP = ip_adress[2:-2].strip()
PORT = 5005

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

print(f"\n(DEBUG) SERVER LISTENING... {IP}:{PORT} \n")

sockets_list = [server_socket]

connected_clients = []

current_users = []
users = ""

clients = {}

message_num = 1

client_socket, client_address = "", ""


def send_user_data(client_soc, conn_clients, users_list):
    global users
    for client_soc in conn_clients:
        for i in range(len(current_users)):
            users = users + users_list[i] + "|-|"
        client_soc.send(bytes(users.encode('utf-8')))
        print("(DEBUG) USERNAME DATA BEING SENT: " + str(users))
        users = ""


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8"))
        print("MSG HEADER: ", message_header)
        print("MSG LENGTH: ", str(message_length))
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)

            connected_clients.append(client_socket)

            clients[client_socket] = user

            print('(DEBUG) RAW USER DATA : ', user['data'].decode('utf-8'))

            print(f"(DEBUG) Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")
            current_users.append("!UnSaEmRe@" + str(user['data']))

            send_user_data(client_socket, connected_clients, current_users)

        else:
            message = receive_message(notified_socket)
            print("(DEBUG) MESSAGE VAR TYPE: " + str(type(message)))
            print("(DEBUG) MESSAGE VAR: " + str(message))
            if message is not False:
                if "!UnSaEmRe@" in message['data'].decode('utf-8'):
                    msg = message['data'].decode('utf-8')
                    msg = msg.replace("!UnSaEmRe@", '')
                    msg = msg.strip()
                    print("(DEBUG) USER: " + msg + " IS LEAVING")
                    connected_clients.remove(notified_socket)
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    for i in range(len(current_users)):
                        if msg in current_users[i]:
                            del current_users[i]
                            break
                    send_user_data(client_socket, connected_clients, current_users)
                else:
                    user = clients[notified_socket]

                    print(f"(DEBUG) Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
                    print(f"(DEBUG) MESSAGE_NUMBER: {str(message_num)} || Sender's IP:ID: {str(notified_socket.getpeername())}")
                    client_num = 0

                    for client_socket in connected_clients:
                        print("(DEBUG) MESSAGE_NUMBER: " + str(message_num) + " || " + "Client's IP:PORT: " + str(
                            connected_clients[client_num].getsockname()) + " | Client's IP:ID: " + str(
                            connected_clients[client_num].getpeername()))
                        client_num += 1
                        print("(DEBUG) SENDING MESSAGE...")
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                        print("(DEBUG) MESSAGE SENT")
                    message_num += 1

            else:
                username = clients[notified_socket]['data'].decode('utf-8').strip()
                print(f"(DEBUG) Closed connection from {username}")
                print("(DEBUG) EXITING USER'S IP: " + client_address[0])
                connected_clients.remove(notified_socket)
                for i in range(len(current_users)):
                    if username in current_users[i]:
                        del current_users[i]
                        break
                send_user_data(client_socket, connected_clients, current_users)
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
