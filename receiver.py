
from socket import *
from packet import *
from math import ceil


server_data_address = 0
server_ack_address = 0
filename = ""
fileSize = 0
totalNumberOfPackets = 0
receivedCount = 0
windowSize = 0
range_sequenceNumber = 65535
base = 0
buffer = dict()
current_sequenceNumber = 0
expectedSequenceNumber = 0

def setWindowSize(size):
    global windowSize
    windowSize = size

def get_filename():
    global filename
    filename = input("Enter file name.")
    return filename


def send_filename(file_name, client_socket, remote_IP, serverPort):
    global filename
    filename = get_filename()
    try:
        print("Trying to send file name")
        client_socket.sendto(filename.encode(), (remote_IP, serverPort))
        client_socket.settimeout(2)
        message, serverAddress = client_socket.recvfrom(2048)
        client_socket.settimeout(None)
        global server_data_address, server_ack_address
        server_data_address = serverAddress
        server_ack_address = (serverAddress[0], serverAddress[1] + 1)
        print("Server Data Address = " + str(server_data_address[1]))
        print("Server ACK Address = " + str(server_ack_address[1]))
    except OSError:
        print("File name was lost")
        return
    if (message.decode())[:6] == "EXISTS":
        try:
            global fileSize, totalNumberOfPackets
            fileSize = int((message.decode())[6:])
            totalNumberOfPackets = ceil(fileSize / 500)
        except ValueError:
            print("Can't retrieve file size")

        respond = input("The file you requested exist, File size = {} kB do you want to download? Y/N ".format(fileSize/1000))
        if respond.upper() == "Y":
            print("Downloading.")
            return "downloading"
        else:
            return"Refusedtodownload"
    elif (message.decode())[:3] == "ERR":
       # print("File not found on the server.")
        return "Filenotfound"


def receive_sr(client_socket, window_size):
    global filename, current_sequenceNumber, windowSize, base
    global server_data_address, expectedSequenceNumber, range_sequenceNumber
    global receivedCount, fileSize, totalNumberOfPackets
    sr_log_recieve=open("SR_LOG_recieve",'w')
    setWindowSize(window_size)
    client_socket.sendto("OK".encode(), server_data_address)
    f = open("new_" + filename, 'wb')
    while base < totalNumberOfPackets:
        while current_sequenceNumber < base + windowSize and receivedCount < totalNumberOfPackets:
            #if receivedCount <= ceil(fileSize / 500):
            data, address = client_socket.recvfrom(508)
            p = Packet()
            p.unpack(data)
            sr_log_recieve.write("Received packet #{}".format(p.sequenceNumber)+"\n")

            #print(receivedCount)
            current_sequenceNumber = p.sequenceNumber
            if p.check_theSum():
                if p.sequenceNumber not in buffer.keys():
                    buffer[p.sequenceNumber] = p.get_components()
                    receivedCount += 1

                p.put_components("".encode())
                ack = p.packetize()
                client_socket.sendto(ack, server_ack_address)

                if p.sequenceNumber == expectedSequenceNumber:
                    """ write data in sequence"""
                    key = expectedSequenceNumber
                    while key in buffer.keys():
                        f.write(buffer[key])
                        buffer.pop(key)
                        key = (key + 1) % range_sequenceNumber
                        expectedSequenceNumber = (expectedSequenceNumber + 1) % range_sequenceNumber
                    base = key
                else:
                    """Don't write anything, leave the data buffered"""
                    pass
            else:
                sr_log_recieve("Packet is corrupted, don't do anything"+"\n")
            #else:
                #break
    sr_log_recieve.write("File transfer completed"+"\n")
    return True