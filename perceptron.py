#!/usr/bin/python2
# coding=utf-8

import gtk, cairo
import sys

from math import ceil, pi

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
	
	def expose(self, widget, event):
		width, height = widget.window.get_size()
		self.cr = cr = widget.window.cairo_create()
		
		cr.set_source_rgb(1, 1, 1)
		cr.rectangle(0, 0, width, height)
		cr.fill()
		
		self.width = width - 45
		self.height = height - 25
		
		self.drawGrid()
		for i in range(self.app.maxLearn):
			self.drawPoint(self.app.net.learning[i])
	
	def drawGrid(self):
		cr = self.cr; width = self.width; height = self.height
		net = self.app.net
	
		cr.set_source_rgb(0, 0, 0)
		cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_NORMAL)
		cr.set_font_size(15)
		
		for x in range(11):
			cr.move_to(x * width / 10, 0)
			cr.rel_line_to(0, height)
			cr.rel_move_to(0, 20)
			cr.show_text(str(x / 10.0 * net.x[0].rangeVal()))
		
		for y in range(11):
			cr.move_to(0, y * height / 10)
			cr.rel_line_to(width, 0)
			cr.rel_move_to(5, 0)
			cr.show_text(str(y / 10.0 * net.x[1].rangeVal()))

		cr.stroke()
	
	def drawPoint(self, point):
		cr = self.cr; width = self.width; height = self.height
		net = self.app.net
		
		x = (point[0] - net.x[0].minVal) / net.x[0].rangeVal() * width
		y = (point[1] - net.x[1].minVal) / net.x[1].rangeVal() * height
		radius = min(width, height) * 0.03
		color = [0, 1, 0] if point[2] == 1 else [1, 0, 0]
		
		cr.set_source_rgb(*color)
		cr.arc(x, y, radius, 0, 2 * pi)
		cr.fill()


class App(gtk.Window):
	
	maxLearn = 0
	maxTest = 0	
	
	def __init__(self, net):
		super(App, self).__init__()
		
		self.net = net
		
		self.set_title("Simulace perceptronu neuronové sítě")
		self.connect("delete-event", gtk.main_quit)
		self.set_border_width(5)
		
		vbox = gtk.VBox(False, 5)
		self.add(vbox)
		
		self.graph = graph = Graph()
		graph.app = self
		graph.connect("expose-event", graph.expose)
		graph.set_size_request(400, 400)
		vbox.pack_start(graph, True)
		
		hbox = gtk.HBox(False, 5)
		hbox.set_size_request(0, 30)
		vbox.pack_start(hbox, False)
		
		self.nextLearningButton = gtk.Button("Pokračovat v učení")
		self.nextLearningButton.connect("clicked", self.nextLearning)
		hbox.add(self.nextLearningButton)
		
		self.nextTestingButton = gtk.Button("Další testovací")
		self.nextTestingButton.connect("clicked", self.nextTesting)
		hbox.add(self.nextTestingButton)
		
		restartButton = gtk.Button("Začít znovu")
		restartButton.connect("clicked", self.restart)
		hbox.add(restartButton)
		
		self.show_all()
	
	def nextLearning(self, widget):
		if self.maxLearn < self.net.learningLen:
			self.maxLearn += 1
		if self.maxLearn >= self.net.learningLen:
			self.nextLearningButton.set_sensitive(False)
		self.queue_draw()
	
	def nextTesting(self, widget):
		if self.maxTest < self.net.testingLen:
			self.maxTest += 1
		if self.maxTest >= self.net.testingLen:
			self.nextTestingButton.set_sensitive(False)
		self.queue_draw()
	
	def restart(self, widget):
		self.maxLearn = self.maxTest = 0
		self.nextLearningButton.set_sensitive(True)
		self.nextTestingButton.set_sensitive(True)
		self.queue_draw()


if __name__ == "__main__":
	try:
		inputFilename = sys.argv[1]
	except:
		print "použití: " + sys.argv[0] + " INPUT_FILE [OUTPUT_FILE]"
		sys.exit(1)

	inputNet = Net()
	inputNet.readInput(inputFilename)

	App(inputNet)
	gtk.main()

