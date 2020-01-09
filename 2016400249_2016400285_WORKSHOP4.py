import os
import sys
import base64
import select
import socket
import threading
from buSocket import buSocket
from datetime import datetime

def responseThreadSummoner(passResponseIP):
    threading.Thread(target=responseThread, args=(passResponseIP,)).start()

def responseThread(responseIP):
    s3 = buSocket(hostIP)
    s3.connect(responseIP,commPort)
    s3.send("[" +userID +", "+hostIP+", "+ "response]")
    s3.close()

def listenUDPThread():
    s4.bind(("", announcePort))
    while not isExit:
        data, addr = s4.recvfrom(1024)
        tempList2 = data.decode('ascii').replace('\n', '')[:-1][1:].split(',',3)
        tempList2[0]= tempList2[0].replace(' ', '')
        tempList2[1]= tempList2[1].replace(' ', '')
        tempList2[2]= tempList2[2].replace(' ', '')
        responseCurrentTimeArray = datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(" ")[1].split(":")
        responseCurrentTime = int(responseCurrentTimeArray[0])*3600 + int(responseCurrentTimeArray[1])*60 + int(responseCurrentTimeArray[2])
        if tempList2[2] == 'announce':
            if tempList2[1] in lastAnnounceTime:
                if (responseCurrentTime - lastAnnounceTime[tempList2[1]])>1:
                    userList[tempList2[0]] = tempList2[1]
                    passerIP = tempList2[1]
                    responseThreadSummoner(passerIP)
                lastAnnounceTime[tempList2[1]] = responseCurrentTime
            else :
                userList[tempList2[0]] = tempList2[1]
                passerIP = tempList2[1]
                responseThreadSummoner(passerIP)
                lastAnnounceTime[tempList2[1]] = responseCurrentTime

def listenThread():
    s = buSocket(hostIP)
    s.bind(commPort)
    while not isExit:
        s.listen()
        receivedData = s.receive()
        if receivedData != "<noConn>":
            tempList = receivedData.replace('\n', '')[:-1][1:].split(',',3)
            tempList[0]= tempList[0].replace(' ', '')
            tempList[1]= tempList[1].replace(' ', '')
            tempList[2]= tempList[2].replace(' ', '')
            if tempList[2] == 'response':
                userList[tempList[0]] = tempList[1]
            elif tempList[2] == 'message':
                tempList[3] = tempList[3].strip()
                if userList[tempList[0]] == tempList[1]:
                    print(tempList[0]+": "+tempList[3])
            elif tempList[2] == 'file':
                tempList2 = tempList[3].split(',', 4)
                if not tempList[1] in recvFiles.keys():
                    recvFiles[tempList[1]]=[]
                recvFiles[tempList[1]].append(tempList2[3])
                if int(tempList2[0])==(int(tempList2[1])-1): #If file is completely received
                    save_file(recvFiles[tempList[1]],tempList2[2])
                    del recvFiles[tempList[1]]


def splitFile(fileContents):
    onePacketSize=10000
    ret=[]
    length = len(fileContents)
    div=length//onePacketSize
    if(div<length/onePacketSize):
        div=div+1
    for i in range(0,div):
        ret.append(fileContents[i*onePacketSize:(i+1)*onePacketSize])
    return ret


def save_file(parts, fileName):
    fileASCII=""
    for i in parts:
        fileASCII=fileASCII+i
    fileContent=base64.b64decode(fileASCII.encode('ascii'))
    file=open(fileName,"wb")
    file.write(fileContent)
    file.close()
    print("The file "+fileName+" is received.")




s4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
currentTimeArray = datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(" ")[1].split(":")
currentTime = int(currentTimeArray[0])*3600 + int(currentTimeArray[1])*60 + int(currentTimeArray[2])
lastTime = 0
lastAnnounceTime = {}
userList = {}
recvFiles = {}
userID = ""
announcePort = 12345
commPort = 12346

isExit = False
hostIP = os.popen('hostname -I').read().replace(" ", "").replace("\n"," ").strip()


pollObject = select.poll()
pollObject.register(sys.stdin.fileno(), select.POLLIN)
print("||2016400285 Barış Zöngür - 2016400249 Galip Ümit Yolcu - CMPE487 - Workshop 4||\n---------------------------\n")
userID = input("What is your username ?\n")
print("This program does not automatically announce you to other users!\nTo announce yourself and start chatting please write -r!\nTo see help on how to use program please write -h")
threading.Thread(target=listenThread,daemon=True).start()
threading.Thread(target=listenUDPThread,daemon=True).start()
while not isExit:
    polledObject = pollObject.poll()
    try:
        polledElement = polledObject.pop()
    except :
        continue
    pollIndex, massage = polledElement
    if pollIndex == sys.stdin.fileno():
        message = sys.stdin.readline().rstrip()
        if message == '-l':
            for key,value in userList.items() :
                print(key)
        elif message == "-h":
            print("-l: List all users currently available\n\n-r: Refreshes your user list and announces you\n")
            print("-m [username]: Will select the user to send message to. Write \"-m\" space and username you want to send message to.\nafter that program will expect you to write your message\n")
            print("-f [username]: Will select the user to send file to. Write \"-m\" space and username you want to send file to.\nafter this, the program will expect you to write the path for the file you want to send. Files will be saved in the directory from which the program is executed in the receiver side.\n")
            print("-e: Exits the program")
        elif message == '-r':
            currentTimeArray = datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(" ")[1].split(":")
            currentTime = int(currentTimeArray[0])*3600 + int(currentTimeArray[1])*60 + int(currentTimeArray[2])
            if currentTime-lastTime > 60:
                userList ={}
                s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s2.settimeout(0.05)
                tempTuple = ("<broadcast>",announcePort)
                s2.bind(("",0))
                s2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
                for i in range(3):
                    s2.sendto(bytes("[" + userID +", "+hostIP+", "+ "announce" +"]", 'ascii'), tempTuple)
                s2.close()
                lastTime=currentTime
            else:
                print(str(60-(currentTime-lastTime))+" seconds remaining to refresh")
        elif message.split(" ", 1)[0] == '-m':
            try:
                messageName = message.split(" ",1)[1]
                messageText = input("to "+messageName+":")
            except:
                print("Faulty message instruction, write -h to help!")
            else:
                try:
                    messageIP = userList[messageName]
                except:
                    print("No such user!")
                else:
                    s2 = buSocket(hostIP)
                    s2.connect(messageIP,commPort)
                    s2.send("[" +userID +", "+hostIP+", "+ "message, " +messageText+"]")
                    s2.close()
        elif message.split(" ", 1)[0] == '-f': #f for File
            try:
                messageName = message.split(" ",1)[1]
                filePath = input("Path to file to send "+messageName+":")
            except:
                print("Faulty message instruction, write -h to help!")
            else:
                if messageName not in userList.keys():
                    print("No such user!")
                else:
                    messageIP = userList[messageName]
                    try:
                        file=open(filePath,'rb')
                        fileContent=base64.b64encode(file.read())
                        file.close()
                    except:
                        print("No such file exists: ("+filePath+")")
                    else:
                        filePackets = splitFile(fileContent)
                        temp=filePath.split('/')
                        fileName=temp[-1]
                        totalPackets = len(filePackets)
                        for p in range(0,totalPackets):
                            s2 = buSocket(hostIP)
                            s2.connect(messageIP,commPort)
                            s2.send("[" +userID + ", " + str(hostIP) + ", " + "file, " + str(p) + ", " + str(totalPackets) + ", " +fileName +", "+filePackets[p].decode('ascii') + "]")
                            s2.close()
                        print("File "+fileName+" sent to "+ messageName)
        elif message == '-e':
            isExit = True
            s4.close()
            exit()
        else :
            print("Faulty instructions, write -h for help!")














