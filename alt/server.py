import socket
import threading

HOST = '127.0.0.1'  # Endereço IP do servidor.
PORT = 8080  # Porta do servidor.
IP_TYPE = socket.AF_INET
SOCK_TYPE = socket.SOCK_STREAM

clients = {}  # Armazenar clientes como {apelido: (IP, conexao)}

def main():
    """Inicia o servidor e aguarda a inscrição dos clientes."""
    server = socket.socket(IP_TYPE, SOCK_TYPE)

    try:
        server.bind((HOST, PORT))
        server.listen()
        print('Servidor iniciado...')
    except:
        print('Erro ao iniciar o servidor.')
        return

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=[client]).start()

def handle_client(client):
    """Gerencia o cadastro e comunicação de cada cliente."""
    try:
        # Receber o apelido e o IP do cliente
        data = client.recv(2048).decode('utf-8').split(",") 
        username, user_ip = data[0], data[1]
        
        # Armazenar o cliente com seu IP
        clients[username] = (user_ip, client)
        broadcast_users()

        # Enviar lista de usuários online ao novo cliente
        send_online_users(client)

        while True:
            msg = client.recv(2048).decode('utf-8')
            if msg.startswith('@'):  # Mensagem privada
                target_username, message = parse_private_message(msg)
                if target_username:
                    send_private_message(username, target_username, message)
                else:
                    client.send('Usuário não encontrado.'.encode('utf-8'))
            else:
                broadcast(f'<{username}> {msg}', client)
    except:
        disconnect_client(username)

def broadcast_users():
    """Atualiza todos os clientes com a lista de usuários online."""
    online_users = ', '.join(clients.keys())
    broadcast(f'Usuários online: {online_users}')

def send_online_users(client):
    """Envia a lista de usuários online a um cliente específico."""
    online_users = ', '.join(clients.keys())
#    client.send(f'Usuários online: {online_users}'.encode('utf-8'))

def send_private_message(sender_username, target_username, message):
    """Envia uma mensagem privada de um cliente para outro."""
    if target_username in clients:
        target_ip, target_client = clients[target_username]
        target_client.send(f'[Privado de {sender_username}]: {message}'.encode('utf-8'))
    else:
        clients[sender_username][1].send(f'O usuário {target_username} está offline.'.encode('utf-8'))

def broadcast(msg, sender_client=None):
    """Envia uma mensagem para todos os clientes."""
    for username, (ip, client) in clients.items():
        if client != sender_client:
            client.send(msg.encode('utf-8'))

def parse_private_message(msg):
    """Extrai o nome de usuário e a mensagem de uma mensagem privada."""
    try:
        target, message = msg.split(' ', 1)
        target_username = target[1:]  # Remove '@'
        return target_username, message
    except ValueError:
        return None, None

def disconnect_client(username):
    """Desconecta um cliente do servidor."""
    if username in clients:
        del clients[username]
        broadcast(f'@{username} saiu do chat!', username)
        broadcast_users()

if __name__ == "__main__":
    main()
