import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para gerenciamento de threads.
import subprocess #Biblioteca para execução de comandos do sistema.

HOST = '127.0.0.1' #Endereço IP do servidor.
PORT = 65432 #Porta de comunicação do servidor.

online_users = dict() #Armazena os nomes de usuário e endereços IP dos clientes.

def main():

    """Inicia o cliente e estabelece a conexão com o servidor."""

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        print(f"Conectado ao servidor {HOST}:{PORT}")
        username = input("Digite o seu nome de usuário: ")
        client.send(username.encode('utf-8'))
        print(client.recv(1024).decode('utf-8'))
    except:
        print("Não foi possível estabelecer conexão com o servidor!")
        exit()
    else:
        threading.Thread(target=receive_messages_from_server, args=(client,), daemon=True).start()
        send_messages_to_server(client)
    finally:
        client.close()
        exit()

def receive_messages_from_server(client):
    
        """Recebe mensagens do servidor."""
    
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message.startswith("<online_users>"):
                    online_users = dict(eval(message.replace("<online_users>", "")))
                    print(f"Usuários online: {', '.join(online_users.keys())}")
                else:
                    print(message)
            except:
                break

def send_messages_to_server(client):
    
        """Envia mensagens para o servidor."""
    
        while True:
            message = input("¬>")
            if message.startswith("@"): 
                """ao digitar @usuário, deverá abrir um novo terminal para conversa privada com o usuário especificado."""
                pass
            client.send(message.encode('utf-8'))
            if message == "exit":
                break

if __name__ == '__main__':
    main()
