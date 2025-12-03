from socket import *

IP = "100.78.169.54"

SEVER_PORT = 50000

BUFLEN = 512

datasocket = socket(AF_INET,SOCK_STREAM)

datasocket.connect((IP,SEVER_PORT))

while True:
    toSend = input(">>>")
    if toSend == "exit":
        break
    datasocket.send(toSend.encode())

    recved = datasocket.recv(BUFLEN)

    if not recved:
        break

    print(recved.decode())

datasocket.close()