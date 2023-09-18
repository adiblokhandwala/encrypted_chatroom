import socket
import threading
import rsa

public_key, private_key = rsa.newkeys(1024)
# Choosing Nickname
nickname = input("Choose your nickname: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))
serverkey = rsa.PublicKey.load_pkcs1(client.recv(2048))
client.send(public_key.save_pkcs1("PEM"))

# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024)
            message = rsa.decrypt(message,private_key).decode('ascii')
            if message == 'NICKNAME':
                client.send(rsa.encrypt(nickname.encode('ascii'),serverkey))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server
def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send(rsa.encrypt(message.encode('ascii'),serverkey))


# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()