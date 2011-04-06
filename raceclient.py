#!/usr/bin/python2
# -*- coding: utf-8 -*-

from backpropnet import *
import socket

# výjimka klientské třídy
class ClientException(Exception):
	def __init__(self, value): self.value = value
	def __str__(self): return repr(self.value)


# třída klienta pro spojení se serverem hry
class RaceClient:

	# parametry připojení:
	server = "127.0.0.1"
	port = "2000"
	race = "zavod"
	driver = "PyDriver"
	color = "a020f0"

	# konstruktor, připojí se k neuronové síti
	def __init__(self, net):
		self.net = net

	# připojí se k serveru
	def connect(self):
		try:
			self.conn = socket.create_connection((self.server, self.port))
			self.conn.send("driver\nrace:" + self.race + "\ndriver:" + \
				self.driver + "\ncolor:" + self.color + "\n\n")
			data = self.conn.recv(1024)
		except Exception as e:
			raise ClientException("Cannot connect: " + str(e))
		if not data.startswith("ok"):
			raise ClientException("Cannot connect, server message: " + data)
		print "Connected"
	
	# uzavře spojení se serverem
	def close(self):
		self.conn.close()
	
	# odehraje jedno kolo
	def play(self):
		try:
			data = self.conn.recv(1024)
		except Exception as e:
			raise ClientException("Cannot read: " + str(e))
		data = data.splitlines()
		if data[0].startswith("finish"):
			print "Game over"
			return False
		if not data[0].startswith("round"):
			raise ClientException("Bad message: " + data[0])
		for item in data[1:]:
			item = item.split(':')
			if len(item) > 1:
				setattr(self, item[0], float(item[1]))
		move = self.net.evaluate([self.distance, self.angle, self.speed, \
			self.distance2])
		try:
			self.conn.send("ok\nacc:" + str(move[0]) + "\nwheel:" + \
				str(move[1]) + "\n\n")
		except Exception as e:
			raise ClientException("Cannot send: " + str(e))
		return True
	
	# hraje, dokud může
	def run(self):
		while self.play():
			pass

