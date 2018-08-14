from threading import *
import server_helpers
import client_helpers
import sender
import receiver

from os import *
def s_GBN(serverSocket,seedvalue,prob,windowsize=10):
    filename, addr = serverSocket.recvfrom(2048)
    print(filename.decode())
    if path.isfile(filename):
        clientThread = Thread(target=server_helpers.return_file_2, args=(filename, addr,seedvalue,prob,windowsize))
        clientThread.start()
        print(active_count())
        print("Done")
        # server_helpers.return_file(filename, serverSocket, addr)
    else:
        serverSocket.sendto("Filenotfound".encode(), addr)

def s_stopandwait(serverSocket,seedvalue,prob):
    filename, addr = serverSocket.recvfrom(2048)
    print(filename.decode())
    if path.isfile(filename):
        clientThread = Thread(target=server_helpers.return_file, args=(filename, addr,seedvalue,prob))
        clientThread.start()
        # server_helpers.return_file(filename, serverSocket, addr)
    else:
        serverSocket.sendto('Filenotfound', addr)

def s_SR(serverSocket, windowSize, seedValue, probability):
    print("Server Started.\nWaiting for requests.")
    filename, address = serverSocket.recvfrom(2048)
    print(seedValue, probability)
    print(filename.decode())
    if path.isfile(filename):
        clientThread = Thread(target=sender.return_file_3, args=(filename, address, seedValue, probability, windowSize))
        clientThread.start()
    else:
        serverSocket.sendto("Filenotfound".encode(), address)


def c_GBN(clientSocket, filename, remoteIP, serverPort, windowsize):
    #filename = client_helpers.get_file_name()
    if not filename:
        clientSocket.close()
        print("client is closing !")
        exit()
    else:
        sent = None
        while sent is None:
            sent = client_helpers.send_file_name(filename, clientSocket, remoteIP, serverPort)

            if sent == "downloading":
                state = client_helpers.recieve_file1(clientSocket)

                if (state):
                    print("File Transfer Completed !")
                else:
                    print("failed to transfer file !")
                    break
            elif sent == "Refusedtodownload":
                print("Refused to download !")
                break
            else:
                print("File Not Found !")
                break

def c_SR(clientSocket, filename, remoteIP, serverPort, window_size):
    #filename = receiver.get_filename()
    if not filename:
        clientSocket.close()
        print("Client Terminated.")
        exit(-1)
    else:
        sent = None
        while sent is None:
            sent = receiver.send_filename(filename, clientSocket, remoteIP, serverPort)
            if sent == 'downloading':
                state = receiver.receive_sr(clientSocket, window_size)

                if state:
                    print("File transfer completed.")
                else:
                    print("Failed to receive file.")
                    break
            elif sent == "Refusedtodwonload":
                print("Refused to Download.")
                break
            else:
                print("File not found.")
                break

def c_stopandwait( clientSocket, filename, remoteIP, serverPort):
    #filename = client_helpers.get_file_name()
    if not filename:
        clientSocket.close()
        print("client is closing !")
        exit()
    else:
        sent = None
        while sent is None:
            sent = client_helpers.send_file_name(filename, clientSocket, remoteIP, serverPort)

            if sent == "downloading":
                state = client_helpers.recieve_file(clientSocket)

                if (state):
                    print("File Transfer Completed !")
                else:
                    print("failed to transfer file !")
                    break
            elif sent == "Refusedtodownload":
                print("Refused to download !")
                break
            else:
                print("File Not Found !")
                break