import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para criação e manipulação de threads.

HOST = '127.0.0.1' #Endereço IP do servidor.
PORT = 8080 #Porta padrão do servidor.
IP_TYPE = socket.AF_INET #Para endereços IPv4.
SOCK_TYPE = socket.SOCK_STREAM #Para conexão TCP. 

clients = {}

def main():

    """Inicia o servidor e aguarda a conexão de clientes."""
    
    server = socket.socket(IP_TYPE, SOCK_TYPE)

    try:
        server.bind((HOST, PORT))
        server.listen()
        print('\nServidor iniciado...')
    except:
        return print('\nNão foi possível iniciar o servidor!\n')
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=[client]).start()

def handle_client(client):

    """Lida com a conexão de um cliente."""

    try:
        username = client.recv(2048).decode('utf-8')

        clients[client] = username
        broadcast(f'@{username} entrou no chat.', client)
        send_online_users(client)

        while True:
            msg = client.recv(2048).decode('utf-8')
            if msg.startswith('@'):  # Mensagem direta
                target_username, message = parse_private_message(msg)
                if target_username:
                    send_private_message(client, target_username, message)
                else:
                    client.send('Usuário não encontrado!'.encode('utf-8'))
            else:
                broadcast(f'<{username}> {msg}', client)
    except:
        disconnect_client(client)

def parse_private_message(msg):

    """Extrai o nome de usuário e a mensagem de uma mensagem privada."""

    try:
        target, message = msg.split(' ', 1)
        target_username = target[1:]  # Remove '@'
        return target_username, message
    except ValueError:
        return None, None

def send_private_message(sender_client, target_username, message):

    """Envia uma mensagem privada de um cliente para outro."""

    for client, username in clients.items():
        if username == target_username:
            sender_username = clients[sender_client]
            client.send(f'[Privado de @{sender_username}]: {message}'.encode('utf-8'))
            #sender_client.send(f'[Privado para {target_username}]: {message}'.encode('utf-8'))
            return
    sender_client.send(f'O usuário @{target_username} está offline!'.encode('utf-8'))

def send_online_users(client):

    """Envia a lista de usuários online para um cliente específico."""

    online_users = ', '.join(clients.values())
    client.send(f'Usuários online: {online_users}'.encode('utf-8'))

def broadcast(msg, sender_client=None):

    """Envia a mensagem para todos os clientes, exceto o remetente."""
    
    for client in clients:
        if client != sender_client:
            try:
                client.send(msg.encode('utf-8'))
            except:
                disconnect_client(client)

def disconnect_client(client):

    """Remove o cliente da lista e informa a todos sobre a desconexão."""

    if client in clients:
        username = clients[client]
        del clients[client]
        broadcast(f'@{username} saiu do chat!', client)
        client.close()

# Inicia o servidor:
if __name__ == "__main__":
    main()