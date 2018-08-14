
from packet import *
from sender import time_out_handler

buffer = []
acks = dict()
p = Packet()
pktsqno = 0

def prepare():
    try:
        global p, pktsqno, buffer
        f = open("bio.pdf", 'rb')
        bytesToSend = f.read(500)
        print(bytesToSend)
        while (bytesToSend != b''):
            if pktsqno != 3:
                p.set_sequenceNumber(pktsqno)
                p.put_components(bytesToSend)
                p.make_sum()
                data = p.packetize()
                #print(data)
                buffer.append(data)
                p.set_checkSum(0)

                bytesToSend = f.read(500)
            else:
                p.set_sequenceNumber(pktsqno)
                p.put_components(bytesToSend)
                data = p.packetize()
                # print(data)
                buffer.append(data)
                p.set_checkSum(0)
                #pktsqno += 1
                bytesToSend = f.read(500)
            pktsqno += 1
    except OSError:
        print("Can't open file")
def recieve():
    try:
        f = open("new_bio.pdf", "wb")

        for i in range(len(buffer)):
            p.set_checkSum(0)
            data = buffer[i]
            p.unpack(data)
            if p.check_theSum():
                print("Packet {} received successfully, Checksum = {}".format(p.get_sequenceNumber(), p.print_sum()))
            else:
                print("Packet {} Corrupted".format(p.get_sequenceNumber()))
            writable = p.get_components()
            f.write(writable)
            #print(writable)

    except OSError:
        print("Can't open file")
prepare()

recieve()



