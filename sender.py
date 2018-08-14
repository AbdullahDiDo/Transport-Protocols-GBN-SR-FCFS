from socket import *
from packet import *
from threading import Lock, Thread
from queue import Empty
import os
from math import ceil
from server_helpers import generate_random_loss_packets


range_sequenceNumber = 65535
windowSize = 0
base = 0
currentSequenceNumber = 0
currentACKSequenceNumber = 0
max_timeout = 0.05
number_of_packets = 0
current_port_number = 5000
fileSize = 0
lock = Lock()
#window = []
#packets = dict()
sendCounter = 0


def setWindowSize(windowsize):
    global windowSize
    windowSize = windowsize

def get_base():
    global base
    return base

def move_base(value):
    global base
    base = value

def generate_sequenceNumber():
    global currentSequenceNumber

    currentSequenceNumber = (currentSequenceNumber + 1) % range_sequenceNumber


def check_windowSize():
    global windowSize, range_sequenceNumber

    if windowSize <= range_sequenceNumber / 2:
        print("Window Size is legit, initializing transmission.")
    else:
        print("Invalid Window Size! Choose window size <= Range of sequence numbers")

def recieveACKS(serverAckSocket,sr_log):
    global base, windowSize, currentACKSequenceNumber
    global sendCounter
    while currentACKSequenceNumber < base + windowSize:
        pack = Packet()
        pack.set_checkSum(0)
        ack, address = serverAckSocket.recvfrom(100)
        pack.unpack(ack)

        if pack.check_theSum():
            lock.acquire(blocking=True)
            sr_log.write("Received ACK on packet #{}".format(pack.sequenceNumber)+"\n")
            pack.ACK()
            currentACKSequenceNumber = pack.sequenceNumber
            if packetList[pack.sequenceNumber] is None:
                sr_log.write("This is repeated ACK"+"\n")
            else:
                pack.add_toList()
            lock.release()
        else:
            sr_log.write("Packet checksum corrupted. do nothing"+"\n")
    serverAckSocket.close()



def setNumberOfPackets(filename):
    global number_of_packets, currentSequenceNumber
    number_of_packets = ceil(os.path.getsize(filename) / 500)


def return_file_3(filename, address, seedValue, probability, window_size):
    global fileSize
    numbers = generate_random_loss_packets(seedValue, probability)
    setWindowSize(window_size)
    sr_log = open("SR_LOG.txt", 'w')
    setLogFile(sr_log)
    new_client_port = generate_port_number()
    server_data_socket = init_server(new_client_port)
    server_ack_socket = init_server(new_client_port + 1)
    server_data_socket.sendto("EXISTS".encode() + str(os.path.getsize(filename)).encode(), address)
    response, address = server_data_socket.recvfrom(2048)
    sr_log.write("User response received"+"\n")
    if response.decode() != "OK":
        print("User request was canceled")
        server_data_socket.close()
        return
    receiving_thread = Thread(target=recieveACKS, args=(server_ack_socket,sr_log))
    receiving_thread.start()
    sendSR(filename, address, server_data_socket, numbers,sr_log)
    receiving_thread.join()


def sendSR(filename, address, serverDataSocket, numbers,sr_log):
    start_time = time.time()
    global number_of_packets, base, windowSize, sendCounter
    setNumberOfPackets(filename)
    sr_log.write("number_of_packets = " + str(number_of_packets)+"\n")
    try:
        f = open(filename, 'rb')
        bytesToSend = f.read(500)
        while bytesToSend != b'':
            while base < number_of_packets:

                while not resendQueue.empty():
                    try:
                        pa = resendQueue.get()
                        pa.set_timeout(max_timeout)
                        resend_p = pa.packetize()
                        pa.start_Timer()
                        serverDataSocket.sendto(resend_p, address)
                        sr_log.write("Packet #{} resent.".format(pa.get_sequenceNumber())+"\n")

                    except Empty:
                        sr_log.write("The Resend Queue is empty. Continue with program flow")
                #lock.acquire(True)
                while currentSequenceNumber < base + windowSize and  sendCounter < number_of_packets:
                    p = Packet()
                    p.put_components(bytesToSend)
                    p.make_sum()
                    p.set_sequenceNumber(currentSequenceNumber)
                    generate_sequenceNumber()
                    p.set_timeout(max_timeout)
                    send_p = p.packetize()
                    #lock.acquire(blocking=True)
                    p.add_toList()
                    p.start_Timer()
                    #lock.release()
                    if sendCounter % 10 not in numbers:
                        serverDataSocket.sendto(send_p, address)
                        sr_log.write("Packet #{} sent.".format(p.get_sequenceNumber())+"\n")
                    sendCounter += 1
                    #p.start_Timer()
                    #print("Packet #{} sent.".format(p.get_sequenceNumber()))
                    bytesToSend = f.read(500)
                    #base = get_baseP()
                    #time.sleep(0.5)
                    #print("inside" + str(base))
                #lock.release()

                #base = getSmallestSeqNum()
                base = get_baseP()
                #print("Outside" + str(base))
                #print("base  = " + str(base))
                #time.sleep(0.5)
    except OSError:
        sr_log.write("File not found."+"\n")
    sr_log.write("file transfer completed"+"\n")
    end_time = time.time()
    sr_log.write("Elapsed Time = {} sec \n".format(end_time - start_time)+"\n")
    serverDataSocket.close()

def generate_port_number():
    global current_port_number
    current_port_number = (current_port_number + 2) % 65535
    return current_port_number


def init_server(port=5000):

    host = gethostbyname('abdullahabdelwahab')
    serverAddress = (host, port)
    serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(serverAddress)
    return serverSocket


# for i in range(7):
#     p = Packet()
#     p.set_sequenceNumber(i)
#     p.set_timeout(max_timeout)
#     if i == 0 or i == 1 or i == 4:
#         p.ACK()
#     p.add_toList()
#     p.start_Timer()
# time.sleep(2)
# packets = getList()
# print(packets)
# for i in packets:
#     packets[i].set_timeout(max_timeout)
#     packets[i].start_Timer()

# check_windowSize()
# set_baseP(0)
# while True:
#     while currentSequenceNumber < (base + windowSize):
#         p = Packet()
#         p.make_sum()
#         p.set_sequenceNumber(currentSequenceNumber)
#         p.add_toList()
#         p.set_timeout(max_timeout)
#         if currentSequenceNumber == 0 or currentSequenceNumber == 3 or currentSequenceNumber == 1:
#             p.ACK()
#         generate_sequenceNumber()
#         p.start_Timer()
#
#
#     time.sleep(0.7)
#     base = get_baseP()
#
#     print(packetList.items())
