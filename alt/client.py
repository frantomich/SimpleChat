import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para gerenciamento de threads.

HOST = '127.0.0.1' #Endereço IP do servidor.
PORT = 65432 #Porta de comunicação do servidor.

online_users = dict() #Armazena os nomes de usuário e endereços IP dos clientes.

def main():

    """Inicia o cliente e estabelece a conexão com o servidor."""

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        print(f"Conectado ao servidor {HOST}:{PORT}")
        username = input("Digite o seu nome de usuário: ")
        client.send(username.encode('utf-8'))
        print(client.recv(1024).decode('utf-8'))
    except:
        print("Não foi possível estabelecer conexão com o servidor!")
        exit()
    else:
        threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
        send_messages(client)
    finally:
        client.close()
        exit()

def receive_messages(client):
    
        """Recebe mensagens do servidor."""
    
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message[0] == "$":
                    online_users = dict(eval(message[1:]))
                    print(f"Usuários online: {', '.join(online_users.keys())}")
                else:
                    print(message)
            except:
                break

def send_messages(client):
    
        """Envia mensagens para o servidor."""
    
        while True:
            message = input("Comando: ")
            if message[0] == "@": 
                """ao digitar @usuário, deverá abrir um novo terminal para conversa privada com o usuário especificado."""
                pass
            client.send(message.encode('utf-8'))
            if message == "exit":
                break

if __name__ == '__main__':
    main()
