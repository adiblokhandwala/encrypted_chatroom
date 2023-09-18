import socket
import threading
import rsa

# Connection Data
host = '127.0.0.1'
port = 55555

public_key, private_key = rsa.newkeys(1024)

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []
client_keys = []

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client_index = clients.index(client)
        client_key = client_keys[client_index]
        client.send(rsa.encrypt(message,client_key))

# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            message = rsa.decrypt(message,private_key)
            broadcast(message)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            client_key = client_keys[index]
            client_keys.remove(client_key)
            break


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        client.send(public_key.save_pkcs1("PEM"))
        client_key = rsa.PublicKey.load_pkcs1(client.recv(2048))
        client_keys.append(client_key)

        # Request And Store Nickname
        client.send(rsa.encrypt('NICKNAME:'.encode('ascii'),client_key))
        nickname = client.recv(1024)
        nickname = rsa.decrypt(nickname,private_key).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send(rsa.encrypt('Connected to server!'.encode('ascii'),client_key))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()             

print(f"chatroom server started at {host} : {port}")
receive()