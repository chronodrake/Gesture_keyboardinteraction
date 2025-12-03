from socket import *

IP = "100.78.169.54"

PORT = 50000

BUFLEN = 512

listensocket = socket(AF_INET,SOCK_STREAM)

listensocket.bind((IP,PORT))

listensocket.listen(5)
print(f"服务端启动成功，正在{IP}{PORT}端口等待客户连接……")

dataSocket,addr = listensocket.accept()

print("接受一个客户端连接：",addr)

while True:
    recved = dataSocket.recv(BUFLEN)

    if not recved:
        break
    
    info = recved.decode()
    print(f"收到了对方消息:{info}")

    dataSocket.send(f"服务端收到了你的消息{info}".encode())

dataSocket.close()
listensocket.close()




