import connection
import techniques
import os

in_remoteIP = 0
in_remotePort = 0
in_filename = ''
in_windowSize = 0

def readInputFile():
    global in_remoteIP, in_remotePort, in_windowSize, in_filename
    inputFile = input("Enter input file name: ")
    if os.path.isfile(inputFile):
        print("File found.")
        with open(inputFile) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            in_remoteIP = content[0]
            in_remotePort = int(content[1])
            in_filename = content[2]
            in_windowSize = int(content[3])
    else:
        print("File not found")
        raise OSError

readInputFile()
#22ra el client.in mn hena ya sa7by w est5dem el line el commented w da5al el server port
remoteIP, clientSocket, serverPort = connection.get_ip_UDPsocket_serverPort(in_remotePort)
#remoteIP, clientSocket, serverPort = connection.get_ip_UDPsocket_serverPort(serverport)

while True:
    choice = int(input("Please select a technique:\n"
                       "1-GBN\n"
                       "2-Selective Reapeat\n"
                       "3-stop & wait\n"))

    if choice == 1:
        techniques.c_GBN( clientSocket, in_filename, remoteIP, serverPort, in_windowSize) # windowsize goes here ya s7by
    elif choice == 2:
        #your code goes here ya sa7by  w sheel pass deh
        techniques.c_SR(clientSocket, in_filename, remoteIP, serverPort, in_windowSize)
    elif choice == 3:
        techniques.c_stopandwait( clientSocket, in_filename, remoteIP, serverPort)
