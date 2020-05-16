import socket
import cv2
import numpy as np
import multiprocessing
import time

IP =  '192.168.0.1'  # IP address of the server 
PORT = 1234          # PORT no should be cross checked with server provider [tested on DigitalOcean]

class Server():
    def __init__(self, ip = IP, port = PORT):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv.bind((ip, port))
        self.serv.listen(2)
        self.names = []
        self.client = []

    def showImg(self,data):
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imshow('server', img)
        cv2.waitKey(0)

    def recvall(self,C):
        BUFF_SIZE = 4096 
        data = b''
        count = 0
        while True:
            part = C.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break

        return data

    def rectext(self,C):
        from_server = C.recv(4096)
        msg = from_server.decode("utf-8")
        return msg

    def makelist(self):
        s = ""
        for name in self.names:
            s += name
            s += '%'
        msg = bytes(s, "utf-8")
        return msg

    def connect(self):
        conn, addr = self.serv.accept()
        print(str(addr) + " is connected")

        self.client.append(conn)

    # def getImg(self):
    #     img = cv2.imread('./NAME.jpg')
    #     frame = cv2.resize(img, (240,320), interpolation = cv2.INTER_AREA)
    #     sdata = cv2.imencode('.jpg', frame)[1].tostring()
    #     return sdata

    def run(self):

        while True:
            
            self.connect()
            start = False   
                
            if len(self.client) == 2:

                n = self.rectext(self.client[0])
                self.names.append(n)
                self.client[0].sendall(bytes('ok', 'utf-8' ))
                n = self.rectext(self.client[1])
                self.names.append(n)
                self.client[1].sendall(bytes('ok', 'utf-8' ))
                start = True

            while start:
                print("got in data zone")
                try:
                    data = self.recvall(self.client)
                    data2 = self.recvall(self.client2)

                    if not data: break
                    if not data2: break

                    self.client.sendall(data2)
                    self.client2.sendall(data)

            """ Testing the server with transfering image """

                    # self.showImg(data)
                    # sdata = b''
                    # sdata += self.getImg()

                    # conn.sendall(sdata)
                    # nparr = np.frombuffer(data, np.uint8)
                    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    # cv2.imshow('server', img)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break

                except:
                    break


                conn.close()
                conn2.close()
                self.names = {}
                print ('client disconnected')
