#!/usr/bin/python2
# coding=utf-8

import gtk, cairo
import sys

from math import ceil, pi
import random

class Net:

	class Input:
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				setattr(self, key, value)
		
		def rangeVal(self):
			return self.maxVal - self.minVal
	
	def readInputFile(self, inputFilename):
	 
		def readLine():
			line = ""
			while line == "" or line.startswith('#'):
				line = inputFile.readline().lstrip()
			return line
		
		inputFile = open(inputFilename, "r")

		self.inputsLen = int(readLine())
		self.inputs = list()
		self.inputs.append(self.Input(name = "nulák",
			minVal = 0.0, maxVal = 1.0))
		for i in range(self.inputsLen):
			name, minVal, maxVal = readLine().split()
			self.inputs.append(self.Input(name = name,
				minVal = float(minVal), maxVal = float(maxVal)))

		self.coeff = float(readLine())

		self.learningLen = int(readLine())
		self.learning = list()
		for i in range(self.learningLen):
			self.learning.append(self.normalizeValues(readLine().split()))

		self.testingLen = int(readLine())
		self.testing = list()
		for i in range(self.testingLen):
			self.testing.append(self.normalizeValues(readLine().split()))

		inputFile.close()
	
	def normalizeValues(self, values):
		newValues = list()
		for i in range(self.inputsLen):
			newValues.append((float(values[i]) - self.inputs[i + 1].minVal) \
				/ self.inputs[i + 1].rangeVal())
		if len(values) > self.inputsLen:
			newValues.append(float(values[self.inputsLen]))
		return newValues
	
	def reset(self):
		for inp in self.inputs:
			inp.weight = random.random()
		self.toLearn = 0
		self.lastAdapt = 0
	
	def evaluate(self, point):
		y = self.inputs[0].weight
		for i in range(1, self.inputsLen + 1):
			y += self.inputs[i].weight * point[i - 1]
		return 1 if y > 0 else 0
	
	def adapt(self, point, sign):
		self.inputs[0].weight += sign * 1
		for i in range(1, self.inputsLen + 1):
			self.inputs[i].weight += sign * point[i - 1]
		self.lastAdapt = 0
	
	def learnMore(self):
		if self.evaluate(self.learning[self.toLearn]) != \
			self.learning[self.toLearn][self.inputsLen]:
			self.adapt(self.learning[self.toLearn], \
				1 if self.learning[self.toLearn][self.inputsLen] == 1 else -1)
		else:
			self.lastAdapt += 1
		self.toLearn += 1
		if self.toLearn == self.learningLen: self.toLearn = 0
	
	def canLearnMore(self):
		return False if self.lastAdapt > self.learningLen else True
	
	def printWeights(self):
		for i in self.inputs:
			print i.weight,
		print


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
		self.drawLine()
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
			cr.show_text(str(x / 10.0 * net.inputs[1].rangeVal() \
				+ net.inputs[1].minVal))
		
		for y in range(11):
			cr.move_to(0, y * height / 10)
			cr.rel_line_to(width, 0)
			cr.rel_move_to(5, 0)
			cr.show_text(str(y / 10.0 * net.inputs[2].rangeVal() \
				+ net.inputs[2].minVal))

		cr.stroke()
	
	def coordsNetToGraph(self, netX, netY):
		width = self.width; height = self.height
		x = netX * width
		y = netY * height
		return max(min(x, width), 0), max(min(y, height), 0)
	
	def drawPoint(self, point):
		cr = self.cr; width = self.width; height = self.height
		
		x, y = self.coordsNetToGraph(point[0], point[1])
		radius = min(width, height) * 0.03
		color = [0, 1, 0] if point[2] == 1 else [1, 0, 0]
		
		cr.set_source_rgb(*color)
		cr.arc(x, y, radius, 0, 2 * pi)
		cr.fill()
	
	def drawLine(self):
		cr = self.cr; inputs = self.app.net.inputs
		
		netY1 = 0
		try: netX1 = -inputs[0].weight / inputs[1].weight \
				- inputs[2].weight / inputs[1].weight * netY1
		except: netX1 = 0
		netY2 = 1
		try: netX2 = -inputs[0].weight / inputs[1].weight \
			- inputs[2].weight / inputs[1].weight * netY2
		except: netX2 = 1
		
		cr.set_source_rgb(0, 0, 1)
		cr.move_to(*self.coordsNetToGraph(netX1, netY1))
		cr.line_to(*self.coordsNetToGraph(netX2, netY2))
		cr.stroke()


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
		
		self.nextLearningButton = gtk.Button("Krokovat učení")
		self.nextLearningButton.connect("clicked", self.nextLearning)
		hbox.add(self.nextLearningButton)
		
		self.learnButton = gtk.Button("Naučit se")
		self.learnButton.connect("clicked", self.learn)
		hbox.add(self.learnButton)
		
		self.nextTestingButton = gtk.Button("Další testovací")
		self.nextTestingButton.connect("clicked", self.nextTesting)
		hbox.add(self.nextTestingButton)
		
		restartButton = gtk.Button("Začít znovu")
		restartButton.connect("clicked", self.restart)
		hbox.add(restartButton)
		
		self.show_all()
		self.net.printWeights()
	
	def nextLearning(self, widget):
		self.net.learnMore()
		self.net.printWeights()
		if self.maxLearn < self.net.learningLen:
			self.maxLearn += 1
		if not self.net.canLearnMore():
			self.nextLearningButton.set_sensitive(False)
		self.queue_draw()
	
	def learn(self, widget):
		while self.net.canLearnMore():
			self.net.learnMore()
		self.maxLearn = self.net.learningLen
		self.queue_draw()
	
	def nextTesting(self, widget):
		if self.maxTest < self.net.testingLen:
			self.maxTest += 1
		if self.maxTest >= self.net.testingLen:
			self.nextTestingButton.set_sensitive(False)
		self.queue_draw()
	
	def restart(self, widget):
		self.net.reset()
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
	
	random.seed()

	inputNet = Net()
	inputNet.readInputFile(inputFilename)
	inputNet.reset()

	App(inputNet)
	gtk.main()

