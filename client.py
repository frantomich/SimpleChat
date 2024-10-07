import socket #Biblioteca para comunicação em rede.
import threading #Biblioteca para criação e manipulação de threads.
import sys #Biblioteca para manipulação de sistema.

HOST = '127.0.0.1' #Endereço IP do servidor.
PORT = 8080 #Porta padrão do servidor.
IP_TYPE = socket.AF_INET #Para endereços IPv4.
SOCK_TYPE = socket.SOCK_STREAM #Para conexão TCP. 

def main():

    """Realiza a conexão com o servidor e inicia as threads para enviar e receber mensagens."""
    
    client = socket.socket(IP_TYPE, SOCK_TYPE)

    try:
        client.connect((HOST, PORT))
    except:
        return print('\nNão foi possível se conectar com o servidor!\n')

    username = input('Nome de usuário ¬> ')
    client.send(username.encode('utf-8'))  # Envia o nome de usuário ao servidor
    print('\nConectado!')

    # Iniciar threads para receber mensagens
    threading.Thread(target=receive_messages, args=[client, username], daemon=True).start()
    
    # Iniciar o envio de mensagens
    send_messages(client, username)

def receive_messages(client, username):
    """Função para receber mensagens do servidor."""
    while True:
        try:
            msg = client.recv(2048).decode('utf-8')
            sys.stdout.write(f'\r{msg}\n')  # Exibe a mensagem recebida
            sys.stdout.write(f'\n<{username}> ')  # Exibe o prompt do usuário
            sys.stdout.flush()
        except:
            print('\nNão foi possível permanecer conectado ao servidor!\n')
            print('\nPressione [Enter] para continuar...\n')
            client.close()
            break

def send_messages(client, username):
    """Função para enviar mensagens ao servidor."""
    while True:
        try:
            sys.stdout.write(f'\n<{username}> ')  # Exibe o prompt do usuário antes de capturar a entrada
            sys.stdout.flush()
            msg = input()  # Captura a mensagem que o usuário deseja enviar
            client.send(msg.encode('utf-8'))
        except:
            return

# Inicia o cliente:
if __name__ == "__main__":
    main()
