import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para gerenciamento de threads.

SERVER_ADDR = '127.0.0.1' #Endereço IP do servidor.
SERVER_PORT = 65432 #Porta de comunicação do servidor.
CLIENT_ADDR = '127.0.0.1' #Endereço IP do cliente.
CLIENT_PORT = 65433 #Porta de comunicação do cliente.

client_username = str() #Armazena o nome de usuário do cliente.
client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Armazena a conexão do cliente com o servidor.

online_users = dict() #Armazena os endereços dos clientes que estiverem online.
online_connections = dict() #Armazena as conexões com os clientes que estiverem online.

def main():
     
    connect_to_server()
    threading.Thread(target=receive_connections, daemon=True).start()
    send_messages()
    for conn in online_connections.values():
        conn.close()
    client_connection.close()
    exit()

def connect_to_server():

    """Inicia o cliente e estabelece a conexão com o servidor."""

    global client_username, client_connection, online_users, online_connections

    try:
        client_connection.connect((SERVER_ADDR, SERVER_PORT))
        print(f"Conectado ao servidor {SERVER_ADDR}:{SERVER_PORT}")
        client_username = input("Digite o seu nome de usuário: ")
        client_connection.send(f"<client>{client_username}:{CLIENT_ADDR}:{CLIENT_PORT}".encode('utf-8'))
        message = client_connection.recv(1024).decode('utf-8')
        if message.startswith("<info>"):
            print(message.replace("<info>", ""))
    except:
        print("Não foi possível estabelecer conexão com o servidor!")
        exit()
    else:
        threading.Thread(target=receive_messages_from_server, args=(client_connection,), daemon=True).start()

def receive_connections():
        
    """Recebe conexões de outros clientes."""

    global client_username, client_connection, online_users, online_connections

    receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        receiver.bind((CLIENT_ADDR, CLIENT_PORT))
        receiver.listen()
        print(f"Recepção de usuários iniciada em {CLIENT_ADDR}:{CLIENT_PORT}")
    except:
        print("Não foi possível iniciar a recepção de usuários!")
        exit()
    else:
        while True:
            conn, addr = receiver.accept()
            message = conn.recv(1024).decode('utf-8')
            if message.startswith("<client>"):
                username, ip, port = message.replace("<client>", "").split(":")
                if username in online_users.keys():
                    online_connections[username] = conn
                    threading.Thread(target=receive_messages_from_client, args=(username,), daemon=True).start()
                    conn.send("<pass>".encode('utf-8'))
                else:
                    conn.send("<erro>".encode('utf-8'))
                    conn.close()
    finally:
        receiver.close()

def connect_to_other_client(username):
    
        """Conecta-se a outro cliente."""

        global client_username, client_connection, online_users, online_connections
    
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            client.connect((online_users[username][0], online_users[username][1]))
            client.send(f"<client>{client_username}:{CLIENT_ADDR}:{CLIENT_PORT}".encode('utf-8'))
            message = client.recv(1024).decode('utf-8')
            if message.startswith("<erro>"):
                return False
            print(f"@{username} conectado!")
            online_connections[username] = client
        except:
             return False
        else:
            threading.Thread(target=receive_messages_from_client, args=(username,), daemon=True).start()
            return True

def receive_messages_from_server(client):
    
        """Recebe mensagens do servidor."""

        global client_username, client_connection, online_users, online_connections
    
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message.startswith("<online_users>"):
                    online_users = dict(eval(message.replace("<online_users>", "")))
                    if len(online_users) > 0:
                        print(f"Usuários online: {', '.join(online_users.keys())}")
                    else:
                        print("Nenhum outro usuário online!")
                else:
                    print(message)
            except:
                break

def receive_messages_from_client(username):
        
        global client_username, client_connection, online_users, online_connections
    
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

    global client_username, client_connection, online_users, online_connections

    while True:
        message = input("¬>")
        if message.startswith("$"):
            client_connection.send(message.encode('utf-8'))
            if message.startswith("$exit"):
                print("Desconectando...")
                break
        if message.startswith("@"):
            is_online = True
            username = message.split()[0][1:]
            username = username.replace("@", "")
            if username not in online_connections.keys():
                is_online = connect_to_other_client(username)
            if is_online:
                online_connections[username].send(message.encode('utf-8'))
            else:
                print(f"Não foi possível conectar-se a @{username}!")

if __name__ == '__main__':
    main()
