import socket

ports = [21, 22, 23, 25, 53, 80, 110, 443, 3306, 8080]
ip = input("ENTER YOUR IP: ")

for i in ports:
    port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port.settimeout(1)
    output = port.connect_ex((ip, i))
    if output == 0:
        print(i, "PORT IS OPEN")
    else:
        print(i, "PORT IS CLOSE")
    port.close()