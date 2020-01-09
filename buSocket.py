import socket


class buSocket:


    def __init__(self,ip):
        self.packetsize = 1500
        self.buffersize = 10
        # 0: initial
        # 1: binded
        # 2: receiving
        # 3: sending
        self.buffer = {}
        self.state = 0
        self.connIP = ""
        self.connPort = ""
        self.receiver_window = 0
        self.leftover = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = 0
        self.windowsize = self.buffersize

    def sendUdp(self, ip, port, message ):
        self.sock.sendto(bytes(message), (ip,port))

    def bind(self, port):
        if(self.state == 0):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.port=port
            self.sock.bind((self.ip, self.port))
            self.sock.settimeout(None)
            self.state = 1
        else:
            print("already bound")

    def listen(self):
        enter_loop = True
        while(enter_loop):
            if self.state == 1:
                data, addr = self.sock.recvfrom(self.packetsize)
                tempList = data.decode('ascii').replace('\n', '')[:-1][1:].split(',',1)
                tempList[0]= tempList[0].replace(' ', '')
                if(tempList[0]=="hist"):
                    self.connIP,self.connPort = addr
                    self.sock.sendto(bytes("(" + "pist,"+ self.ip +"," + str(self.port)+","+ str(self.windowsize)+")", 'ascii'), addr)
                    self.state = 2
            if(self.state == 2):
                data, addr = self.sock.recvfrom(self.packetsize)
                tempList = data.decode('ascii').replace('\n', '')[:-1][1:].split(',',1)
                tempList[0]= tempList[0].replace(' ', '')
                if(tempList[0]=="send"):
                    tempList2 = tempList[1].split(',',3)
                    if(tempList2[0]==self.connIP):
                        self.windowsize = self.windowsize -1
                        self.sock.sendto(bytes("(" + "ok,"+ self.ip +"," + str(self.port)+","+str(self.windowsize)+","+tempList2[1]+")", 'ascii'), addr)
                        recMsgId=int(tempList2[1])
                        self.buffer[recMsgId] = tempList2[3]
                        if(len(self.buffer)==self.buffersize or len(self.buffer)==int(tempList2[2]) or len(self.buffer)==self.leftover):
                            self.leftover = int(tempList2[2]) - len(self.buffer)
                            enter_loop = False
                if(tempList[0]=="bb"):
                    if(tempList[1]==self.connIP):
                        self.sock.sendto(bytes("(" + "kib,"+ self.ip +"," + str(self.port)+")", 'ascii'), addr)
                        self.refresh()
                        enter_loop = False


    def receive(self):
        returnString = ""
        if self.state == 2:
            self.windowsize=self.buffersize
            self.sock.sendto(bytes("(" + "update,"+ self.ip +"," + str(self.port)+","+ str(self.windowsize)+")", 'ascii'), (self.connIP,self.connPort))
            for key in sorted(self.buffer.keys()):
                returnString = returnString + self.buffer[key]
            self.buffer={}
        else:
            returnString="<noConn>"
        return returnString

    def connect(self, ip, port):
        while(self.state <=1):
            i=0
            self.sock.settimeout(1)
            needToSend=True
            while needToSend and i<3:
                self.sock.sendto(bytes("(" + "hist,"+ self.ip+")", 'ascii'), (ip,port))
                try:
                    data, addr = self.sock.recvfrom(self.packetsize)
                    tempList = data.decode('ascii').replace('\n', '')[:-1][1:].split(',',1)
                    tempList[0]= tempList[0].replace(' ', '')
                    if(tempList[0]=="pist"):
                        tempList2 = tempList[1].split(',',2)
                        if(tempList2[0]== ip ):
                            needToSend=False
                            self.connIP = ip
                            self.connPort =port
                            self.receiver_window = int(tempList2[2])
                            self.state = 3
                except socket.timeout:
                    i=i+1
                    if i>2:
                        self.state=4

    def send(self,message):
        if(self.state==3):
            msgs = self.split(message)
            total_packet_size =len(msgs)
            ack_packets = {}
            in_flight = {}
            will_send = 0
            i=0
            self.sock.settimeout(1)
            while(len(ack_packets)<total_packet_size and i <3):
                while(len(in_flight)<self.receiver_window and will_send<total_packet_size):
                    self.sock.sendto(bytes("(" + "send,"+ self.ip +","+ str(will_send)+","+str(total_packet_size)+","+msgs[will_send].decode('ascii')+")", 'ascii'), (self.connIP,self.connPort))
                    in_flight[will_send] = True
                    will_send = will_send +1
                try:
                    data, addr = self.sock.recvfrom(self.packetsize)
                    tempList = data.decode('ascii').replace('\n', '')[:-1][1:].split(',',1)
                    tempList[0]= tempList[0].replace(' ', '')
                    if(tempList[0]=="ok"):
                        tempList2 = tempList[1].split(',',3)
                        if(tempList2[0]== self.connIP):
                            if(int(tempList2[3]) in in_flight.keys()):
                                del in_flight[int(tempList2[3])]
                            i=0
                            ack_packets[int(tempList2[3])] = True
                            self.receiver_window = int(tempList2[2])
                    if(tempList[0]=="update"):
                        tempList2 = tempList[1].split(',',2)
                        if(tempList2[0]== self.connIP):
                            i=0
                            self.receiver_window = int(tempList2[2])
                except socket.timeout:
                    i=i+1
                    if i>2:
                        self.state=4
                    for k in in_flight.keys():
                        self.sock.sendto(bytes("(" + "send,"+ self.ip +"," + str(k)+","+str(total_packet_size)+","+msgs[k].decode('ascii')+")", 'ascii'), (self.connIP,self.connPort))


    def split(self,message):
        message_byte = bytes(message , encoding="ascii")
        message_length = len(message_byte)
        ret={}
        newPacket =self.packetsize -50
        packet_num=message_length//newPacket
        if(packet_num<message_length/newPacket):
            packet_num = packet_num +1
        for i in range(0,packet_num):
            ret[i] = message_byte[i*newPacket:newPacket*(i+1)]
        return ret

    def refresh(self):
        self.buffer ={}
        self.state = 1
        self.connIP=""
        self.connPort=0
        self.receiver_window = 0
        self.leftover = 0

    def close(self):
        i=0
        if self.state!=4:
            needToSend=(self.state>1)
            self.sock.settimeout(1)
            while needToSend and i<3:
                self.sock.sendto(bytes("(" + "bb,"+ self.ip +")", 'ascii'), (self.connIP,self.connPort))
                try:
                    data, addr = self.sock.recvfrom(self.packetsize)
                    tempList = data.decode('ascii').replace('\n', '')[:-1][1:].split(',',1)
                    if(tempList[0]=="kib"):
                        needToSend=False
                except socket.timeout:
                    i=i+1

        self.refresh()
        self.state=0
