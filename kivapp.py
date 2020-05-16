import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button 
from kivy.uix.screenmanager import ScreenManager , Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

import os
import cv2
import sys
import socket 
import numpy as np
from client import Client
import multiprocessing
import time

wsClient = None

IP =  '192.168.0.1'  # IP address of the server 
PORT = 1234    

class firstPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 2

		self.add_widget(Label(text = "IP :"))
		self.ip = TextInput(text = IP ,multiline = False)
		self.add_widget(self.ip)

		self.add_widget(Label(text = "port :"))
		self.port = TextInput(text = PORT, multiline = False)
		self.add_widget(self.port)

		self.nameb = Label(text = "username :")
		self.add_widget(self.nameb)
		self.uname = TextInput(text = 'tronrover', multiline = False)
		self.add_widget(self.uname)

		self.add_widget(Label(text = ""))

		self.join = Button(text = 'Join',background_down = "./img/1.png", background_normal = "./img/5.png")
		self.join.bind(on_press = self.joinButton)
		self.add_widget(self.join)

	def joinButton(self, instance):
		ip = self.ip.text 
		port = self.port.text
		uname = self.uname.text
		info = f"Waiting for other to Join"	

		sapp.second.update(info)

#  here we change the screen from first to second
		sapp.screen_manager.current = 'second'

		Clock.schedule_once(self.connect, 1)

	def connect(self, _):
		port = int(self.port.text)
		ip = self.ip.text 
		uname = self.uname.text

		global wsClient
		wsClient = Client(ip = ip, port = port)
		if wsClient.connected == False :
			# should show error here
			errorMsg()
			return 

		wsClient.sendText(uname)

		sapp.makechat()
		sapp.screen_manager.current = 'chat'



class PreChat(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.names = wsClient.recText()
		self.call = False

		self.cols = 1
		self.rows = 5

		self.add_widget(Label(height = Window.size[1]*0.30, size_hint_y = None))

		self.name1 = GridLayout(cols = 3)
		self.name1.add_widget(Label(width = Window.size[0]*0.3, size_hint_x = None))
		self.button1 = Button(background_normal = "./img/1.png",text = self.names[0])
		self.name1.add_widget(self.button1)
		self.name1.add_widget(Label())
		self.add_widget(self.name1)

		self.name2 = GridLayout(cols = 3)
		self.name2.add_widget(Label(width = Window.size[0]*0.3, size_hint_x = None))

		try:
			self.button2 = Button(background_normal = "./img/2.png",text = self.names[1])
		except:
			self.button2 = Button(background_normal = "./img/2.png",text = "")

		self.name2.add_widget(self.button2)
		self.name2.add_widget(Label())
		self.add_widget(self.name2)

		self.add_widget(Label(height = Window.size[1]*0.30, size_hint_y = None))


		Clock.schedule_once(self.makecall, 2)

	# def updateNames(self, _):
	"""    need an idea to fix this    """
		# self.names = wsClient.recText()
		# for names 

	def checkcall(self):
		msg = wsClient.recvall()
		msg = msg.decode("utf-8")
		print(msg)
		if msg == 'call':
			self.call = True


	def makecall(self, _):

		p = multiprocessing.Process(target=self.checkcall)
		p.start()
		p.join(1)
		
		if self.call:
			sapp.makechat()
			sapp.screen_manager.current = 'chat'




class secondPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1

		self.message = Label(halign = 'center', valign = 'middle', font_size = 30)
		self.message.bind(width = self.updateWidth)
		self.add_widget(self.message)

	def update(self, msg):
		self.message.text = msg

	def updateWidth(self, *_):
		self.message.text_size = (self.message.width * 0.9, None)



class showChat(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.capture = cv2.VideoCapture(0)
 
		self.cols = 2
		self.rows = 1

		self.other = Image(width = Window.size[0]*0.8, size_hint_x = None)
		# self.other = Label(width = Window.size[0]*0.8, size_hint_x = None)
		self.add_widget(self.other)

		side = GridLayout(rows = 2)

		self.me = Image()
		side.add_widget(self.me)
		side.add_widget(Label(height = Window.size[1]*0.70, size_hint_y = None))

		self.add_widget(side)

		Clock.schedule_interval(self.update, 1.0/10.0)

	def update(self, _):
		ret, frame = self.capture.read()
		encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
		result, encimg = cv2.imencode('.jpg', frame, encode_param)
		decimg = cv2.imdecode(encimg, 1)


		# cv2.imshow('img', decimg)

		frame = cv2.resize(decimg, (240,320), interpolation = cv2.INTER_AREA)
		buf1 = cv2.flip(frame, 0)
		buf = buf1.tostring()
		# print(buf)

		global wsClient

		rec = wsClient.sendImg(frame)
		rec = cv2.resize(rec, (480,640), interpolation = cv2.INTER_AREA)
		bufrec1 = cv2.flip(rec, 0)
		bufrec = bufrec1.tostring()
		

		texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
		texture2 = Texture.create(size=(480, 640), colorfmt='bgr') 

		texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
		texture2.blit_buffer(bufrec, colorfmt='bgr', bufferfmt='ubyte')


		self.me.texture = texture1
		self.other.texture = texture2


	def sendMsg(self, _):
		print("do something to client to send msg")
		


def errorMsg():
	sapp.second.update('No connection to server !')
	sapp.screen_manager.current = 'second'
	Clock.schedule_once(sys.exit, 3)



class firstApp(App):
	def build(self):
		self.screen_manager = ScreenManager()

		self.first = firstPage()
		screen = Screen(name = 'first')
		screen.add_widget(self.first)
		self.screen_manager.add_widget(screen)

		self.second = secondPage()
		screen = Screen(name = 'second')
		screen.add_widget(self.second)
		self.screen_manager.add_widget(screen)

		return self.screen_manager

	def makechat(self):
		self.chat = showChat()
		screen = Screen(name = 'chat')
		screen.add_widget(self.chat)
		self.screen_manager.add_widget(screen)

	def makeprechat(self):
		self.prechat = PreChat()
		screen = Screen(name = 'prechat')
		screen.add_widget(self.prechat)
		self.screen_manager.add_widget(screen)





sapp = firstApp()
sapp.run()