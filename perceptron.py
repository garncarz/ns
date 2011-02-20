#!/usr/bin/python2
# coding=utf-8

import pygtk
import gtk, cairo
import sys

from math import ceil

class Net:

	class X:
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				setattr(self, key, value)
		
		def rangeVal(self):
			return self.maxVal - self.minVal
	
	def readInput(self, inputFilename):
	 
		def readLine():
			line = ""
			while line == "" or line.startswith('#'):
				line = inputFile.readline().lstrip()
			return line
		
		inputFile = open(inputFilename, "r")

		self.xLen = int(readLine())
		self.x = list()
		for i in range(self.xLen):
			name, minVal, maxVal = readLine().split()
			self.x.append(self.X(name = name,
				minVal = float(minVal), maxVal = float(maxVal)))

		self.coeff = float(readLine())

		self.learningLen = int(readLine())
		self.learning = list()
		for i in range(self.learningLen):
			self.learning.append([float(item) for item in readLine().split()])

		self.testingLen = int(readLine())
		self.testing = list()
		for i in range(self.testingLen):
			self.testing.append([float(item) for item in readLine().split()])

		inputFile.close()


class Graph(gtk.DrawingArea):
	
	__gsignals__ = {"expose-event": "override"}

	def do_expose_event(self, event):
		self.draw(*self.window.get_size())
	
	def draw(self, width, height):
		content = self.window.cairo_create()
	
		content.set_source_rgb(0, 0.8, 0)
		content.rectangle(0, 0, width, height)
		content.fill()
		
		content.set_source_rgb(1, 0, 1)
		for x in range(int(ceil(net.x[0].rangeVal()))):
			content.move_to(x * width / net.x[0].rangeVal(), 0)
			content.line_to(x * width / net.x[0].rangeVal(), height)
		content.stroke()
		
		content.set_source_rgb(0.2, 4, 0.6)
		for y in range(int(ceil(net.x[1].rangeVal()))):
			content.move_to(0, y * height / net.x[1].rangeVal())
			content.line_to(width, y * height / net.x[1].rangeVal())
		content.stroke()


try:
	inputFilename = sys.argv[1]
except:
	print "použití: " + sys.argv[0] + " INPUT_FILE [OUTPUT_FILE]"
	sys.exit(1)

net = Net()
net.readInput(inputFilename)

window = gtk.Window()
window.set_title("Neuron network perceptron simulation")
window.connect("delete-event", gtk.main_quit)

area = Graph()
window.add(area)

window.show_all()
gtk.main()

