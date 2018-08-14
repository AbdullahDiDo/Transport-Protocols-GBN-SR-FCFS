import struct
import math
import time
HEADER_FORMAT = '!HHI'
fileSize=None
server_address=0
filename=""
counter =0
WindowSize=0
def get_file_name():
    global filename
    filename = input("Please enter Filename or Enter to quit \n")
    return filename
def send_file_name(filename, clientSocket, remoteIP, serverPort):
    try:
        print("trying to send Filename !")
        filename=get_file_name()
        clientSocket.sendto(filename.encode(), (remoteIP, serverPort))
        clientSocket.settimeout(2)
        message, serveraddress = clientSocket.recvfrom(2048)
        global server_address
        server_address=serveraddress
    except OSError:
        print("Filename was Lost !")
        return
    if (message.decode())[:6] == "EXISTS":
        try:
            global fileSize
            fileSize = int((message.decode())[6:])
        except ValueError:
            print("couldn't retrieve filesize")
        response = input("File exists and its size= {} do you want to download it y/n ".format(fileSize))
        if response.upper() == "Y":
            print("downloading file...")
            return "downloading"
        else:
            return "Refusedtodownload"
    elif (message.decode())[:3] == "ERR":
        return "Filenotfound"


def recieve_file(clientSocket):
    start_time = time.time()
    stop_wait_log_reciever = open("STOP_WAIT_LOG_receiver.txt", 'w')
    clientSocket.sendto("OK".encode(), (server_address))
    try:
        f = open("new_"+filename, "wb")
        data, address = clientSocket.recvfrom(508)               #8bytes header + 500 bytes message
        pkt_cksum, pkt_len, pkt_seqno, packet_contents = unpack(data)
        total_recieved = len(packet_contents)
        f.write(packet_contents)
        ACK = make_pkt(pkt_cksum, pkt_len, pkt_seqno, "") # need to claculate checksum and pkt_len
        stop_wait_log_reciever.write("PACKET" + str(pkt_seqno) + "recieved"+"\n")
        clientSocket.sendto(ACK, server_address)
        ack_seq_no=pkt_seqno
        stop_wait_log_reciever.write("ACK" + str(ack_seq_no) + "sent"+"\n")
        ack_seq_no=0
        while total_recieved < fileSize :
            try:
                global counter
                counter += 1
                data, address = clientSocket.recvfrom(508)  # 8bytes header + 500 bytes message
                pkt_cksum, pkt_len, pkt_seqno, packet_contents = unpack(data)
                stop_wait_log_reciever.write("PACKET" + str(pkt_seqno) + "recieved"+"\n")
                prev=ack_seq_no
                ack_seq_no=pkt_seqno
                if(ack_seq_no == prev):#duplicate packet send with prev Ackseq_no
                    ACK = make_pkt(pkt_cksum, pkt_len, pkt_seqno, "")  # need to claculate checksum and pkt_len
                    print(pkt_cksum)
                    clientSocket.sendto(ACK, server_address)
                    continue
                total_recieved += len(packet_contents)
                stop_wait_log_reciever.write("TOTAL RECEIEVED: "+str(total_recieved)+"FILE SIZE :"+str(fileSize)+"\n")
                f.write(packet_contents)
                ACK = make_pkt(pkt_cksum, pkt_len, pkt_seqno, "")  # need to claculate checksum and pkt_len
                ack_seq_no=pkt_seqno
                clientSocket.sendto(ACK,server_address)
                stop_wait_log_reciever.write("ACK" + str(ack_seq_no) + "sent"+"\n")
                if len(packet_contents) < 500:
                    return True

            except OSError:
                continue

    except IOError:
        print("cannot open file")
    end_time=time.time()
    stop_wait_log_reciever.write("File Recieved Total Elapsed time {}".format(end_time-start_time)+"\n")
    return True
def recieve_file1(clientSocket,windowsize=10):
    global WindowSize
    clientSocket.sendto("OK".encode(), (server_address))
    expected_seq_no=0
    total_recieved =0
    start_time = time.time()
    GBN_log_reciever = open("GBN_LOG_reciever.txt", 'w')
    #w = int(input("Please Enter WindowSize"))
    Set_windowSize(windowsize)
    number_of_packets=math.ceil(int(fileSize) / 500)
    count = 0
    try:
        f = open("new_"+filename, "wb")
        while expected_seq_no <number_of_packets :
            try:
                data, address = clientSocket.recvfrom(508)  # 8bytes header + 500 bytes message
                pkt_cksum, pkt_len, pkt_seqno, packet_contents = unpack(data)
                GBN_log_reciever.write("PACKET" + str(pkt_seqno) + "recieved"+"\n")
                if expected_seq_no==int(pkt_seqno):
                    ACK = make_pkt(pkt_cksum, pkt_len, expected_seq_no, "")  # need to claculate checksum and pkt_len
                    clientSocket.sendto(ACK, server_address)
                    f.write(packet_contents)
                    total_recieved+=len(packet_contents)
                    GBN_log_reciever.write("Total Recieved :"+str(total_recieved)+"filsize:"+str(fileSize)+"\n")
                    expected_seq_no = expected_seq_no + 1
                else:
                    GBN_log_reciever.write("Packet not recieved in order"+str(expected_seq_no)+"was expected"+"\n")
                    ACK = make_pkt(pkt_cksum, pkt_len, (expected_seq_no-1), "")  # need to claculate checksum and pkt_len
                    clientSocket.sendto(ACK, server_address)
            except OSError:
                GBN_log_reciever.write("Cannot Recieve"+"\n")
    except IOError:
        print("cannot open file")
    expected_seq_no=0
    end_time=time.time()
    GBN_log_reciever.write("Transfer Completed Total Elapsed Time = {} secs".format(end_time-start_time)+"\n")
    return True


def unpack(data):
    header = data[:8]
    pkt_cksum, pkt_len, pkt_seqno = struct.unpack(HEADER_FORMAT, header)
    packet_contents = data[8:]
    return pkt_cksum, pkt_len, pkt_seqno, packet_contents


def make_pkt(pkt_cksum, pkt_len, pkt_seqno, packet_contents):
    header = struct.pack(HEADER_FORMAT, pkt_cksum, pkt_len, pkt_seqno)
    return header+packet_contents.encode()
def check_ACK_no(ack_no,pkt_no):
    if(ack_no==pkt_no):
        return True
    else:
        return False

def Set_windowSize(w):
    global WindowSize
    WindowSize = w
