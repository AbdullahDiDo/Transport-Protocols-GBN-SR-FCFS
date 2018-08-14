import struct
from threading import Timer,Lock
from queue import Queue

import time
from typing import TextIO

HEADER_FORMAT = "!HHI"
packetList = dict()
lock = Lock()
largest_ack_sequence_number = 0
baseP = 0
resendQueue = Queue()

def setLogFile(filename):
    global sr_log
    sr_log=filename


def getQueue():
    return resendQueue

def getSmallestSeqNum():
    global smallest_unacked_seqnum
    return smallest_unacked_seqnum

def set_baseP(value):
    global baseP
    baseP = value
def get_baseP():
    global baseP
    return baseP

def getList():
    global packetList
    return packetList

class Packet():

    def __init__(self):
        self.sequenceNumber = 0
        self.components = b''
        self.sumdata = str (self.sequenceNumber) + str (self.components) + str(self.length)
        self.Acknowledgment = False
        self.checkSum = 0
        self.lengthp = 0
        self.time_out = 0
        pass


    def add_toList(self):
        packetList[self.sequenceNumber] = self

    def remove_fromList(self):
        packetList.pop(self.sequenceNumber)


    def start_Timer(self):
        global logFile
        t = Timer((self.time_out),function=self.time_out_handler)
        t.start()
        sr_log.write("Started timeout, Packet #{}".format(self.sequenceNumber)+"\n")

    def time_out_handler(self):
        lock.acquire(blocking=True)
        global packetlist, baseP, largest_ack_sequence_number
        seqNum = self.sequenceNumber
        pack = packetList[self.sequenceNumber]
        if pack.check_ACK() == True:
            #lock.acquire(blocking=True)
            sr_log.write("Packet {} Acked, removing from list".format(self.sequenceNumber)+"\n")
            self.remove_fromList()
            if self.sequenceNumber > largest_ack_sequence_number:
                largest_ack_sequence_number = self.sequenceNumber
                sr_log.write(str(largest_ack_sequence_number)+"\n")
            if not packetList:
                baseP = largest_ack_sequence_number + 1
            else:
                baseP = list(packetList.keys())[0]
                sr_log.write(str(packetList.keys())+"\n")
                sr_log.write(str(baseP)+"\n")


            # if baseP == self.sequenceNumber:
            #     print("HERE")
            #     baseP = list(packetList.keys())[0]
            #     #baseP = baseP + 1
            #     print(baseP)
            # elif packetList.keys() is not None:
            #     print(packetList.keys())
            #     baseP = list(packetList.keys())[0]
            #     print(baseP)
            #lock.release()

        else:
            #lock.acquire(blocking=True)
            sr_log.write("Packet #{} unACKED".format(self.sequenceNumber))
            resendQueue.put(item=self,timeout=None)
            sr_log.write("Placed Packet #{} in the resend Queue.".format(self.sequenceNumber))
            if packetList:
                baseP = list(packetList.keys())[0]
                sr_log.write(str(packetList.keys())+"\n")
                sr_log.write(str(baseP)+"\n")
            else:
                baseP = largest_ack_sequence_number + 1
            #print(smallest_unacked_seqnum)
            #lock.release()
        lock.release()

    def set_sequenceNumber(self, sequenceNumber):
        self.sequenceNumber = sequenceNumber

    def set_timeout(self, value):
        self.time_out = value

    def get_sequenceNumber(self):
        return self.sequenceNumber

    def set_checkSum(self, checkSum):
        self.checkSum = checkSum

    def get_checkSum(self):
        return self.checkSum

    def put_components(self, packetComponents):
        self.components = packetComponents
        self.lengthp = len(packetComponents)

    def get_components(self):
        return self.components

    def length(self):
        self.lengthp = len(self.components)
        return self.lengthp

    def ACK(self):
        self.Acknowledgment = True

    def check_ACK(self):
        if self.Acknowledgment:
            return True
        else:
            return False

    def packetize(self):
        header = struct.pack(HEADER_FORMAT, self.checkSum, self.lengthp, self.sequenceNumber)
        return header + self.components

    def unpack(self, data):
        header = data[:8]
        self.checkSum, self.length, self.sequenceNumber = struct.unpack(HEADER_FORMAT, header)
        self.components = data[8:]

    def make_sum(self):

        #sentBytes = len(bytesToSend)
        #sum_data = str(bytesToSend) + str(sentBytes) + str(nextseqno)
        #check_sum = get_checksum(sum_data)

        i = len(self.sumdata)

        # Handle the case where the length is odd
        if i & 1:
            i -= 1
            sumx = ord(self.sumdata[i])
        else:
            sumx = 0

        # Iterate through chars two by two and sumx their byte values
        while i > 0:
            i -= 2
            sumx += (ord(self.sumdata[i + 1]) << 8) + ord(self.sumdata[i])

        # Wrap overflow around
        sumx = (sumx >> 16) + (sumx & 0xffff)

        result = (~ sumx) & 0xffff  # One's complement
        result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
        self.checkSum = result

    def check_theSum(self):
        i = len(self.sumdata)

        # Handle the case where the length is odd
        if i & 1:
            i -= 1
            sumx = ord(self.sumdata[i])
        else:
            sumx = 0

        # Iterate through chars two by two and sumx their byte values
        while i > 0:
            i -= 2
            sumx += (ord(self.sumdata[i + 1]) << 8) + ord(self.sumdata[i])

        # Wrap overflow around
        sumx = (sumx >> 16) + (sumx & 0xffff)

        result = (~ sumx) & 0xffff  # One's complement
        result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes

        if result == self.checkSum:
            return True
        else:
            return False

    def print_sum(self):
        return str(self.checkSum)

    def __str__(self):
        return "Packet #" + str(self.sequenceNumber)

    def __repr__(self):
        return "Packet #" + str(self.sequenceNumber)

    def __lt__(self, other):
        return self.sequenceNumber < other.get_sequenceNumber()
    def __le__(self, other):
        return self.sequenceNumber <= other.get_sequenceNumber()
    def __gt__(self, other):
        return self.sequenceNumber > other.get_sequenceNumber()
    def __ge__(self, other):
        return self.sequenceNumber >= other.get_sequenceNumber()
    def __eq__(self, other):
        return self.sequenceNumber == other.get_sequenceNumber()
    def __ne__(self, other):
        return self.sequenceNumber != other.get_sequenceNumber()