import socket #Biblioteca para comunicação em rede.
import netifaces #Biblioteca para obter informações de rede.
import threading #Biblioteca para gerenciamento de threads.

SERVER_IP = '127.0.0.1' #Endereço IP padrão do servidor.
SERVER_PORT = 65432 #Porta de comunicação padrão do servidor.

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define o tipo de conexão usada pelo servidor (IPv4, TCP).
clients = dict() #Armazena o endereço IP e porta dos clientes.
connections = dict() #Armazena as conexões com os clientes.

def main():

    """Função principal do servidor."""

    global SERVER_IP

    SERVER_IP = get_ip()

    srv = threading.Thread(target=init_server, daemon=True)
    srv.start()

    cmd = threading.Thread(target=prompt, daemon=True)
    cmd.start()

    cmd.join()
    exit(0)

def get_ip():
    
        """Obtém o endereço IP do servidor a partir da interface de rede selecionada."""
    
        interfaces = netifaces.interfaces()
        print("\nSelecione a interface de rede onde o servidor irá operar:\n")
        for i, interface in enumerate(interfaces):
            print(f"\t{i} - {interface}")
        while True:
            try:
                index = int(input("\nSelecione a interface de rede: "))
                interface = interfaces[index]
                ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            except:
                print("\nInterface inválida ou indisponível!")
            else:
                return ip

def init_server():

    """Inicia o servidor e aguarda a conexão de clientes."""

    global server

    try:
        server.bind((SERVER_IP, SERVER_PORT))
        server.listen()
        print(f"\nServidor escutando em {SERVER_IP}:{SERVER_PORT}\n")
    except:
        print("\nNão foi possível iniciar o servidor!\n")
        server.close()
        exit(0)
    else:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def handle_client(conn, addr):

    """Estabelece a conexão com os clientes."""

    global clients, connections

    message = conn.recv(1024).decode('utf-8')
    if message.startswith("<client>"):
        username, ip, port = message.replace("<client>", "").split(":")
    clients[username] = (ip, int(port))
    connections[username] = conn
    print(f"Conexão estabelecida com {username} ¬> {addr[0]}:{addr[1]}\n")
    conn.send(f"<pass>".encode('utf-8'))
    for cli in clients:
        send_online_users(cli)
    while True:
        message = conn.recv(1024).decode('utf-8')
        if message.startswith("$update"):
            send_online_users(username)
        if message.startswith("$exit"):
            for c in connections.values():
                c.send(f"<offline>{username}".encode('utf-8'))
            break
    print(f"Usuário {username} desconectado!\n")
    del clients[username]
    del connections[username]
    conn.close()
    for cli in clients:
        send_online_users(cli)

def send_online_users(username):

    """Envia a lista de usuários online para o cliente."""

    global clients, connections

    online_users = clients.copy()
    del online_users[username]
    connections[username].send(f"<online_users>{online_users}".encode('utf-8'))

def prompt():

    """Exibe o prompt do servidor."""

    global server, clients, connections

    while True:
        #command = input("¬> ")
        command = input()
        if command.startswith("exit"):
            for conn in connections.values():
                conn.close()
            server.close()
            break
        elif command.startswith("users"):
            if not clients:
                print("\nNenhum usuário online!\n")
            else:
                print("\nUsuários online:\n")
                for user in clients:
                    print(f"{user} ¬> {clients[user][0]}:{clients[user][1]}")
                print()
        else:
            print("Comando inválido!")

if __name__ == "__main__":
    main()
