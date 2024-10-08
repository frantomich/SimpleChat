import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para gerenciamento de threads.

HOST = '127.0.0.1' #Endereço IP do servidor.
PORT = 65432 #Porta de comunicação do servidor.

clients = dict() #Armazena os nomes de usuário e endereços IP dos clientes.
connections = dict() #Armazena as conexões com os clientes.

def main():

    """Inicia o servidor e aguarda a conexão de clientes."""

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Servidor escutando em {HOST}:{PORT}")
    except:
        print("Não foi possível iniciar o servidor!")
        exit()
    else:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    finally:
        server.close()
        exit()

def handle_client(conn, addr):

    """Estabelece a conexão com o cliente."""

    try:
        username = conn.recv(1024).decode('utf-8')
        clients[username] = addr
        connections[username] = conn
        print(f"Conexão estabelecida com @{username} ¬> {addr[0]}:{addr[1]}")
        conn.send("Conexão estabelecida com sucesso!".encode('utf-8'))
        send_online_users(username)
    except:
        print("Erro ao estabelecer conexão com o cliente!")
        conn.close()
    while True:
        try:
            message = conn.recv(1024).decode('utf-8')
            if message.startswith("\update"):
                send_online_users(username)
            if message.startswith("\exit"):
                break
        except:
            break
    print(f"Usuário @{username} desconectado!")
    del clients[username]
    del connections[username]
    conn.close()

def send_online_users(username):

    """Envia a lista de usuários online para o cliente."""

    online_users = clients.copy()
    del online_users[username]
    connections[username].send(f"<online_users>{str(online_users)}".encode('utf-8'))

if __name__ == "__main__":
    main()
