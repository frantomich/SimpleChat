import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para gerenciamento de threads.

SERVER_IP = '127.0.0.1' #Endereço IP do servidor.
SERVER_PORT = 2000 #Porta de comunicação do servidor.

CLIENT_IP = '127.0.0.1' #Endereço IP do cliente.
CLIENT_PORT = 2001 #Porta de comunicação do cliente.

client_username = str() #Armazena o nome de usuário do cliente.

client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define o tipo de conexão usada para comunicação com o servidor (IPv4, TCP).
receiver_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define o tipo de conexão usada para recepção de mensagens de outros clientes (IPv4, TCP).

online_users = dict() #Armazena os endereços dos clientes que estiverem online.
online_connections = dict() #Armazena as conexões com os clientes que estiverem online.

def main():

    """Função principal do cliente."""

    global client_username

    client_username = input("\nDigite o seu nome de usuário: ")

    connect_to_server()
    threading.Thread(target=init_receiver, daemon=True).start()
    send_messages()

    exit(0)

def connect_to_server():

    """Inicia o cliente e estabelece a conexão com o servidor."""

    global client_username, client_connection

    try:
        client_connection.connect((SERVER_IP, SERVER_PORT))
        print(f"\nConectado ao servidor {SERVER_IP}:{SERVER_PORT}\n")
        client_connection.send(f"<client>{client_username}:{CLIENT_IP}:{CLIENT_PORT}".encode('utf-8'))
        message = client_connection.recv(1024).decode('utf-8')
        if message.startswith("<pass>"):
            print("Conexão estabelecida com sucesso!\n")
        else:
            raise Exception
    except:
        print("\nNão foi possível estabelecer conexão com o servidor!\n")
        client_connection.close()
        exit(0)
    else:
        threading.Thread(target=receive_messages_from_server, daemon=True).start()

def connect_to_guest(username):
    
    """Conecta-se a outro cliente."""

    global client_username, online_users, online_connections

    guest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        guest.connect((online_users[username][0], online_users[username][1]))
        guest.send(f"<client>{client_username}:{CLIENT_IP}:{CLIENT_PORT}".encode('utf-8'))
        message = guest.recv(1024).decode('utf-8')
        if message.startswith("<erro>"):
            return False
        print(f"\nUsuário(a) {username} conectado(a)!\n")
        online_connections[username] = guest
    except:
            guest.close()
            return False
    else:
        threading.Thread(target=receive_messages_from_guest, args=(username,), daemon=True).start()
        return True

def init_receiver():
        
    """Recebe conexões de outros clientes."""

    global receiver_connection

    try:
        receiver_connection.bind((CLIENT_IP, CLIENT_PORT))
        receiver_connection.listen()
        print(f"Recepção de usuários iniciada em {CLIENT_IP}:{CLIENT_PORT}\n")
    except:
        print("Não foi possível iniciar a recepção de usuários!\n")
        receiver_connection.close()
        exit(0)
    else:
        while True:
            conn, addr = receiver_connection.accept()
            threading.Thread(target=handle_guest, args=(conn, addr), daemon=True).start()

def handle_guest(conn, addr):

    """Gerencia as conexões de outros clientes."""

    global online_users, online_connections

    message = conn.recv(1024).decode('utf-8')
    if message.startswith("<client>"):
        username, ip, port = message.replace("<client>", "").split(":")
        if username in online_users:
            if online_users[username] == (ip, int(port)):
                online_connections[username] = conn
                print(f"Conexão recebida de {username} ¬> {addr[0]}:{addr[1]}\n")
                conn.send("<pass>".encode('utf-8'))
                threading.Thread(target=receive_messages_from_guest, args=(username,), daemon=True).start()
        else:
            conn.send("<erro>".encode('utf-8'))
            conn.close()


def receive_messages_from_server():
    
    """Recebe mensagens do servidor."""

    global client_connection, online_users

    while True:
        try:
            message = client_connection.recv(1024).decode('utf-8')
            if message.startswith("<online_users>"):
                online_users = dict(eval(message.replace("<online_users>", "")))
                if len(online_users) > 0:
                    print(f"Usuários online: {', '.join(online_users.keys())}\n")
                else:
                    print("Nenhum outro usuário online!\n")
            elif message.startswith("<offline>"):
                username = message.replace("<offline>", "")
                if username in online_connections:
                    online_connections[username].close()
                    del online_connections[username]
                    print(f"Usuário(a) {username} desconectado(a)!\n")
            else:
                print(message)
        except:
            break

def receive_messages_from_guest(username):
        
    global online_connections

    """Recebe mensagens de outros clientes."""

    while True:
        try:
            message = online_connections[username].recv(1024).decode('utf-8')
            if message:
                print(f"<{username}>: {message}\n")
        except:
            break

def send_messages():
    
    """Envia mensagens para o servidor ou outros clientes."""

    global client_connection, receiver_connection, other_connection, online_connections

    while True:
        #message = input("¬> ")
        message = input("")
        if message.startswith("$"):
            client_connection.send(message.encode('utf-8'))
            if message.startswith("$exit"):
                print("\nDesconectando...\n")
                for conn in online_connections.values():
                    conn.close()
                client_connection.close()
                receiver_connection.close()
                break
        elif message.startswith("@"):
            is_online = True
            message = message.replace("@", "")
            username = message.split()[0]
            message = message.replace(f"{username} ", "")
            if username not in online_connections:
                is_online = connect_to_guest(username)
            if is_online:
                online_connections[username].send(message.encode('utf-8'))
            else:
                print(f"\nNão foi possível conectar-se com o usuário {username}!\n")
        else:
            print("Comando inválido!\n")

if __name__ == '__main__':
    main()
