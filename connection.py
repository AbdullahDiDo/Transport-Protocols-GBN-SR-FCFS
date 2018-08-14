import socket

def get_ip_UDPsocket_serverPort(serverport=5000):
    try:
        remoteIP = socket.gethostbyname("abdullahabdelwahab")
        serverPort = 5000
        UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        print("here")
        return remoteIP, UDPsocket, serverPort
    except OSError:
        print("cannot make socket !")
        exit()


def init_server(port=5000):

    host = socket.gethostbyname('MuhammadKorra')
    serverAddress = (host, port)
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(serverAddress)

    return serverSocket





if __name__=="__main__":
    import  doctest
    doctest.testmod()