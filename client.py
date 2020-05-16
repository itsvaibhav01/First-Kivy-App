import socket
import numpy as np
import cv2

IP =  '192.168.0.1'  # IP address of the server 
PORT = 1234    

class Client():
	def __init__(self, ip = IP, port = PORT):
		try:
			self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client.connect((ip, port))
			self.connected = True
			self.msg = ''
		except:
			self.connected = False

	def recvall(self):
	    BUFF_SIZE = 4096 
	    data = b''
	    count = 0
	    while True:
	        part = self.client.recv(BUFF_SIZE)
	        data += part
	        if len(part) < BUFF_SIZE:
	        	break

	    return data


	def sendImg(self, img):
		try:
			frame = cv2.resize(img, (240,320), interpolation = cv2.INTER_AREA)
			sdata = cv2.imencode('.jpg', frame)[1].tostring()
			self.client.sendall(sdata)


			from_server = self.recvall()
			self.msg = from_server

			nparr = np.frombuffer(self.msg, np.uint8)
			img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
			return img
		except:
			self.client.close()

	def sendText(self, msg):
		m = msg
		mm = bytes(m,"utf-8")
		self.client.send(mm)
		m = self.client.recv(4096)
		m.decode('utf-8')
		print(m)

	
	def recText(self):
		from_server = self.recvall()
		msg = from_server.decode("utf-8")

		names = list(msg.split('%'))
		names = list(filter(lambda x:len(x) != 0, names))
		return names