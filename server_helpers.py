from socket import *
import math
import os
import struct
import threading
from timer import Timer
import time
import random
HEADER_FORMAT = '!HHI'
pkt_seqnum = 0
fileSize =0
counter=0
WindowSize=0
current_port_number =1023
sndpkt=dict()
base=0
nextseqno=0
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 0.3
number_of_packets =0
lock=threading.Lock()
send_timer = Timer(TIMEOUT_INTERVAL)
completed=False
def init_server(port=5000):

    host = gethostbyname('abdullahabdelwahab')
    serverAddress = (host, port)
    serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(serverAddress)
    return serverSocket


def return_file(filename, address,seedvalue,prob): #put the server socket instance
    start_time=time.time()
    stop_wait_log=open("STOP_WAIT_LOG.txt",'w')
    new_port_number=generate_port_number()
    numbers=generate_random_loss_packets(seedvalue,prob)
    server_socket_data=init_server(new_port_number)
    global fileSize
    fileSize = os.path.getsize(filename)
    server_socket_data.sendto("EXISTS".encode() + str(fileSize).encode(), address)
    userResponse, address = server_socket_data.recvfrom(2048)
    userResponse = userResponse.decode('utf8')
    while( userResponse[:2] != 'OK'):
        pass
    f = open(filename, 'rb')
    bytesToSend = f.read(500)
    sentBytes=len(bytesToSend)
    global pkt_seqnum
    sum_data = str(bytesToSend) + str(sentBytes) + str(pkt_seqnum)
    check_sum = get_checksum(sum_data)
    packet = make_packet(check_sum, sentBytes, pkt_seqnum, bytesToSend)
    Acked=False
    count =0
    while not Acked:
        try:
            server_socket_data.settimeout(0.5)
            if count not in numbers:
                server_socket_data.sendto(packet, address)
                stop_wait_log.write("PACKET"+str(pkt_seqnum)+"sent"+"\n")
            else:
                stop_wait_log.write("PACKET" + str(pkt_seqnum) + "not sent"+"\n")
            ack, address = server_socket_data.recvfrom(8) #waits for ack
            ack_cksum,ack_len,ack_seqno,ack_contents=unpack(ack)
            stop_wait_log.write("ACK" + str(ack_seqno) + "recieved"+"\n")
            check=check_ACK_no(ack_seqno,pkt_seqnum)
        except OSError:
            stop_wait_log.write("packet was Lost !")
            count+=1
            continue
        Acked=True
    while (check == False): #do nothing
        ack, address = server_socket_data.recvfrom(100)  # waits for ack
        ack_cksum, ack_len, ack_seqno, ack_contents = unpack(ack)
        check = check_ACK_no(ack_seqno, pkt_seqnum)
    bytesToSend = f.read(500)

    while (bytesToSend != (b'')):
        count+=1
        pkt_seqnum =(pkt_seqnum+1)%2
        sentBytes = len(bytesToSend)
        sum_data = str(bytesToSend) + str(sentBytes) + str(pkt_seqnum)
        check_sum = get_checksum(sum_data)
        packet = make_packet(check_sum,sentBytes, pkt_seqnum, bytesToSend)
        Acked = False
        while not Acked:
            try:
                server_socket_data.settimeout(0.5)
                if (count%10) not in numbers :
                    server_socket_data.sendto(packet, address)
                    stop_wait_log.write("PACKET" + str(pkt_seqnum) + "sent"+"\n")
                else :
                    stop_wait_log.write("PACKET" + str(pkt_seqnum) + "not sent"+"\n")
                ack, address = server_socket_data.recvfrom(100)  # waits for ack
                ack_cksum, ack_len, ack_seqno, ack_contents = unpack(ack)
                stop_wait_log.write("ACK" + str(ack_seqno) + "recieved"+"\n")
            except OSError:
                stop_wait_log.write("packet was Lost !"+"\n")
                count += 1
                continue
            Acked = True
        while (int(ack_seqno) == int((pkt_seqnum-1))): #wait for correct ack
            try:
                stop_wait_log.write("waiting for ACK")
                ack, address = server_socket_data.recvfrom(8)  # waits for ack
                ack_cksum, ack_len, ack_seqno, ack_contents = unpack(ack)
            except OSError:
                stop_wait_log.write("TIME OUT !/Resending")
                continue
            count+=1
        bytesToSend = f.read(500)
    stop_wait_log.write("TRANSFER COMPLETED !")
    end_time=time.time()
    stop_wait_log.write("Elapsed Time = {} secs".format(end_time-start_time)+"\n")
    server_socket_data.close()




def return_file_2(filename, address,seedvalue,prob,windowsize): #put the server socket instance
    start_time = time.time()
    GBN_log = open("GBN_LOG.txt", 'w')
    Set_windowSize(windowsize)
    new_port_number=generate_port_number()
    numbers=generate_random_loss_packets(seedvalue,prob) # have to add seedvalue and prob must be passed from above
    server_socket_data=init_server(new_port_number)
    global fileSize
    global number_of_packets
    fileSize = os.path.getsize(filename)
    number_of_packets=math.ceil(int(fileSize)/500)
    GBN_log.write("number of packets:"+str(number_of_packets))
    server_socket_data.sendto("EXISTS".encode() + str(fileSize).encode(), address)
    userResponse, address = server_socket_data.recvfrom(2048)
    userResponse = userResponse.decode('utf8')
    while( userResponse[:2] != 'OK'):
        pass
    Reciving_Thread = threading.Thread(target=GBN_rcv, args=(server_socket_data,GBN_log))
    Reciving_Thread.start()
    GBN_send(filename,address,server_socket_data,numbers,GBN_log)
    GBN_log.write("Total time elapsed =  {} secs".format(time.time()-start_time))
def GBN_send(filename,address,server_socket_data,numbers,GBN_log):
    global lock
    global base
    global nextseqno
    global send_timer
    global sndpkt
    global WindowSize
    global pkt_seqnum
    global completed
    global number_of_packets
    base=0
    nextseqno=0
    try:
        f = open(filename, 'rb')  # read first packets up to windowsize
        bytesToSend = f.read(500)
        count=0
        while (bytesToSend != (b'')):
            while base < number_of_packets:
                lock.acquire()
                while nextseqno<base+WindowSize:
                    count = count + 1
                    sentBytes = len(bytesToSend)
                    sum_data = str(bytesToSend) + str(sentBytes) + str(nextseqno)
                    check_sum = get_checksum(sum_data)
                    if nextseqno not in sndpkt.keys():
                        sndpkt[nextseqno]=(make_packet(check_sum, sentBytes, nextseqno, bytesToSend))
                    if (count %10) not in numbers  :
                        GBN_log.write("next sequence number"+str(nextseqno) +"\n")
                        server_socket_data.sendto(sndpkt[nextseqno], address)
                        GBN_log.write("PACKET" + str(nextseqno) + "sent")
                        GBN_log.write("length of bytes" + str(len(bytesToSend)) +"\n")
                        nextseqno = nextseqno + 1
                    else:
                        GBN_log.write("-PACKET" + str(nextseqno) + "not sent sent" +"\n")
                        nextseqno = nextseqno + 1
                    bytesToSend = f.read(500)
                if not send_timer.running() : # if first packet or if recieved an ack
                    GBN_log.write('Starting timer' +"\n")
                    send_timer.start()
                while send_timer.running() and not send_timer.timeout(): #timer goes off or got an ack
                    lock.release()
                    GBN_log.write('Sleeping' +"\n")
                    time.sleep(SLEEP_INTERVAL)
                    lock.acquire()
                if  send_timer.timeout(): # if packet was lost
                    send_timer.stop()

                    for i in range(base,nextseqno): # resend packets or make nextseqno = base
                        server_socket_data.sendto(sndpkt[i], address)
                        GBN_log.write("Resending Packet" + str(i) + "sent" +"\n")
                        GBN_log.write("length of bytes" + str(len(bytesToSend)) +"\n")
                        #if not send_timer.running():  # if first packet or if recieved an ack
                            #print('Starting timer')    #########################################
                            #send_timer.start()
                   # nextseqno=base

                lock.release()
                GBN_log.write("Done transfering"+"\n")
    except ValueError:
        print(bytesToSend)
        print("Cannot Open File")
    return



def GBN_rcv(server_socket_data,GBN_log):
    global lock
    global nextseqno
    global base
    global completed
    global  number_of_packets
    while base < number_of_packets :
        ack, address = server_socket_data.recvfrom(100)  # waits for ack
        ack_cksum, ack_len, ack_seqno, ack_contents = unpack(ack) # we have to check for corrpution here in chksum
        GBN_log.write("ACK" + str(ack_seqno) + "recieved"+"\n")
        if(int(ack_seqno)>=base):
            lock.acquire()
            base=int(ack_seqno)+1
            send_timer.stop()
            lock.release()
    GBN_log.write("Transfer Completed Closing connection"+"\n")

    return

def Set_windowSize(w):
    global WindowSize
    WindowSize=w


def make_packet(pkt_chksum, pkt_len, pkt_seqnum, pkt_contents):
    header = struct.pack(HEADER_FORMAT, pkt_chksum, pkt_len, pkt_seqnum)
    return header + pkt_contents

def unpack(data):
    header = data[:8]
    pkt_cksum,pkt_len,pkt_seqno= struct.unpack(HEADER_FORMAT, header)
    packet_contents = data[8:].decode()
    return pkt_cksum,pkt_len,pkt_seqno,packet_contents
def get_checksum(data):
    i = len(data)

    # Handle the case where the length is odd
    if i & 1:
        i -= 1
        sumx = ord(data[i])
    else:
        sumx = 0

    # Iterate through chars two by two and sumx their byte values
    while i > 0:
        i -= 2
        sumx += (ord(data[i + 1]) << 8) + ord(data[i])

    # Wrap overflow around
    sumx = (sumx >> 16) + (sumx & 0xffff)

    result = (~ sumx) & 0xffff  # One's complement
    result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
    return result
def check_ACK_no(ack_no,pkt_no):
    if(ack_no==pkt_no):
        return True
    else:
        return False
def generate_port_number():
    global current_port_number
    current_port_number=(current_port_number+1) % 65535
    return current_port_number

def generate_random_loss_packets(seedvalue, prob):
    random.seed(seedvalue)
    number_of_lost_packets = prob*10
    numbers=set()
    chosen=0
    while number_of_lost_packets > 0:
        number=random.randrange(0,10)
        if number not in numbers:
            numbers.add(number)
            number_of_lost_packets-=1
    return numbers