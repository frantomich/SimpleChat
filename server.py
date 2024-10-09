import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para gerenciamento de threads.

HOST = '127.0.0.1' #Endereço IP do servidor.
PORT = 65432 #Porta de comunicação do servidor.

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define o tipo de conexão usada pelo servidor (IPv4, TCP).
CLIENTS = dict() #Armazena o endereço IP e porta dos clientes.
CONNECTIONS = dict() #Armazena as conexões com os clientes.

def main():

    """Função principal do servidor."""

    srv = threading.Thread(target=init_server, daemon=True)
    srv.start()

    cmd = threading.Thread(target=prompt, daemon=True)
    cmd.start()

    cmd.join()
    exit(0)

def init_server():

    """Inicia o servidor e aguarda a conexão de clientes."""

    try:
        SERVER.bind((HOST, PORT))
        SERVER.listen()
        print(f"Servidor escutando em {HOST}:{PORT}\n")
    except:
        print("Não foi possível iniciar o servidor!")
        SERVER.close()
        exit(0)
    else:
        while True:
            conn, addr = SERVER.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def handle_client(conn, addr):

    """Estabelece a conexão com os clientes."""

    message = conn.recv(1024).decode('utf-8')
    if message.startswith("<client>"):
        username, ip, port = message.replace("<client>", "").split(":")
    CLIENTS[username] = (ip, int(port))
    CONNECTIONS[username] = conn
    print(f"Conexão estabelecida com {username} ¬> {addr[0]}:{addr[1]}\n")
    conn.send(f"<pass>".encode('utf-8'))
    for c in CLIENTS:
        send_online_users(c)
    while True:
        message = conn.recv(1024).decode('utf-8')
        if message.startswith("$update"):
            send_online_users(username)
        if message.startswith("$exit"):
            break
    print(f"Usuário {username} desconectado!\n")
    del CLIENTS[username]
    del CONNECTIONS[username]
    conn.close()

def send_online_users(username):

    """Envia a lista de usuários online para o cliente."""

    online_users = CLIENTS.copy()
    del online_users[username]
    CONNECTIONS[username].send(f"<online_users>{online_users}".encode('utf-8'))

def prompt():

    """Exibe o prompt do servidor."""

    while True:
        command = input()
        if command.startswith("exit"):
            for conn in CONNECTIONS:
                print("oi")
                conn.send(f"<exit>".encode('utf-8'))
            SERVER.close()
            break
        elif command.startswith("users"):
            print("Usuários online: ")
            for user in CLIENTS:
                print(f"{user} ¬> {CLIENTS[user][0]}:{CLIENTS[user][1]}")
            print("\n")
        else:
            print("Comando inválido!\n")

if __name__ == "__main__":
    main()
