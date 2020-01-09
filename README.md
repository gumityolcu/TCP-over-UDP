2016400249 Galip Ümit Yolcu
2016400285 Barış Zöngür
Workshop 4

Program written in: Python 3.7.4 Ubuntu 18.04

-Program does not create new window for each chat.
-Program does not announce automatically when program starts. You have to manually write -r to announce in the program. 
-You announce to yourself too. You can see yourself in list of people.
-Inside the program press -h to get help for using the program

==============================================

Our TCP-like socket level protocol:

Buffer size is not customizable and is 1500*10 bytes

HIŞT packets: We perform 2-way handshake. The connecting computer sends
 (hist, <sender-IP>) 
to the listening socket.

PIŞT packets: The listener sends back 
(pist, <listener-IP>, <listener-Port>, <receive window size>)
when a HIŞT packet is received.

SEND packets: Used for transmitting data. Sender sends
(send,<sender-IP>,<part-no>,<total-parts>,<content>)
to the listener where part-no is the id of the packet that is currently being sent and <total-parts> is the total number of packets in the message currently being sent

OK packets: Analoguous to ACK packets in TCP.
Receiver sends back
(ok,<listener-IP>,<listener-Port>,<current-receive-window>,<part-no>)
where <part-no> is the id of the packet that has been received

UPDATE packets: Used for directly sending information about the receive window to the sender side when a read operation has been called in the application layer.
(update,<listener-IP>,<listener-Port>,<current-receive-window>)

BB packets: Used by the sender to end communication
Sender sends
(bb,<sender-IP>)

KIB packets: Used for acknowledging BB packets by the listener side:
(kib,<listener-IP>,<listener-Port>)


All packets are always less than 1500 bytes. If a message requires greater packets, it is split to multiple packets.

The sender waits for 1 second to get acknowledgement for HIŞT, SEND or BB packets. If no acknowledgement(PIŞT, OK or KIB packets) is returned, it tries 3 times before it closes the connection.

The class has 7 relevant methods to be used in the application layer:

1- Constructor buSocket(<IP>)
The IP of the host should be given

2- bind(<port>)
Used by listener sockets

3- listen()
Used to listen until a whole message is received or the buffer is full

4- receive()
Used to retrieve the buffer contents

5- connect(<listener-IP>, <listener-Port>)
Used by sender sockets to connect to remote listener sockets

6- send(<data>)
Used to send data to remote listener sockets. Data should be ASCII encoded string

7- close()
Used to close connection by sender sockets.

So a typical sender socket is used as:

socket = buSocket(<myIp>)
socket.connect(<remoteIP>,<remotePort>)
while <condition>:
	socket.send(<data>)
socket.close()

And a typical listener socket is used as:

socket = buSocket(<myIP>)
socket.bind(<myPort>)
while <condition>:
	socket.listen()
	data=socket.receive()

=============================================================

We added a new packet type to the application level protocol:

[<userName>,<userIP>,file,<part_no>,<total_parts>,<file_name>,<content>]

We use base64 encoding to send the data. Once converted to ASCII characters by base64 encoding, the data is split in 10000 character chunks and each part is sent with the packet schema given above.

When all packets are received, they are decoded, combined in a single file which is saved to the directory where the script runs with the name <file_name>.


