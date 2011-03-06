#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Simulace perceptronu neuronové sítě
# Autor: Ondřej Garncarz, 2011
# Program je napsán v jazyce Python, využívá prostředí GTK a grafického nástroje
# Cairo.
# Spouští se následovně:
# python perceptron.py <vstup> - poté spustí interaktivní GUI pro daný vstupní
#   soubor s možností se učit a testovat
# python perceptron.py <vstup> <výstup> - poté se automaticky naučí ze vstupního
#   souboru a výsledky testování bodů vypíše do výstupního souboru

import gtk, cairo
import sys

from math import ceil, pi
import random


# třída neuronové sítě o jednom perceptronu
class Net:

	# třída vstupu perceptronu
	class Input:
	
		# konstruktor, přiřadí vlastnostem vstupu přijaté hodnoty
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				setattr(self, key, value)
		
		# vrátí rozsah hodnot daného vstupu
		def rangeVal(self):
			return self.maxVal - self.minVal
	
	# načte informace popisující a testující perceptron z daného souboru
	def readInputFile(self, inputFilename):
	 
	 	# vrátí následující informativní řádku souboru
		def readLine():
			line = ""
			while line == "" or line.startswith('#'):
				line = inputFile.readline().lstrip()
			return line
		
		inputFile = open(inputFilename, "r")

		self.inputsLen = int(readLine())  # počet vstupů perceptronu
		self.inputs = list()  # vstupy perceptronu
		self.inputs.append(self.Input(name = "nulák",  # první je fixní
			minVal = 0.0, maxVal = 1.0))  # s nasyceným příjmem
		for i in range(self.inputsLen):  # ostatní vstupy
			name, minVal, maxVal = readLine().split()
			self.inputs.append(self.Input(name = name,
				minVal = float(minVal), maxVal = float(maxVal)))

		self.coeff = float(readLine())  # koeficient učení

		self.learningLen = int(readLine())  # počet učících bodů
		self.learning = list()  # učící body
		for i in range(self.learningLen):
			self.learning.append(self.normalizeValues(readLine().split()))

		self.testingLen = int(readLine())  # počet testovaných bodů
		self.testingOrig = list()  # originální zadání testovaných bodů
		self.testing = list()  # testované body s normalizovanými hodnotami
		for i in range(self.testingLen):
			line = readLine().split()
			self.testingOrig.append(line)
			self.testing.append(self.normalizeValues(line))

		inputFile.close()
	
	# vrátí normalizované hodnoty bodu pro rozsah <0, 1>
	def normalizeValues(self, values):
		newValues = list()
		for i in range(self.inputsLen):
			newValues.append((float(values[i]) - self.inputs[i + 1].minVal) \
				/ self.inputs[i + 1].rangeVal())
		if len(values) > self.inputsLen:
			newValues.append(float(values[self.inputsLen]))
		return newValues
	
	# vynuluje učení perceptronu, nastaví váhy vstupů na náhodné hodnoty
	def reset(self):
		for inp in self.inputs:
			inp.weight = random.random()
		self.toLearn = 0
		self.lastAdapt = 0
	
	# vyhodnotí daný bod podle toho, co se zatím naučil
	def evaluate(self, point):
		y = self.inputs[0].weight
		for i in range(1, self.inputsLen + 1):
			y += self.inputs[i].weight * point[i - 1]
		return 1 if y > 0 else 0
	
	# postoupí ve fázi učení
	def learnMore(self):
		delta = self.learning[self.toLearn][self.inputsLen] - \
			self.evaluate(self.learning[self.toLearn])
		if delta != 0:
			# adaptace
			self.inputs[0].weight += delta * self.coeff * 1
			for i in range(1, self.inputsLen + 1):
				self.inputs[i].weight += delta * self.coeff * \
					self.learning[self.toLearn][i - 1]
			self.lastAdapt = 0  # kroků od poslední adaptace
		else:
			self.lastAdapt += 1
		self.toLearn += 1  # další bod k učení se
		if self.toLearn == self.learningLen: self.toLearn = 0
	
	# vrátí, zda-li je možné se ještě něco naučit
	def canLearnMore(self):
		return False if self.lastAdapt > self.learningLen else True
	
	# vrátí řetězec ohledně hodnot vah vstupů
	def showWeights(self):
		return "weights: " + "".join(map(lambda x: \
			"%4.3f" % x.weight + ' ', self.inputs))
	
	# vrátí řetězec výsledku testování daného bodu
	def showTesting(self, nr):
		return "".join(map(lambda x: x + ' ', self.testingOrig[nr])) + \
			str(self.evaluate(self.testing[nr]))
	
	# naučí perceptron a vypíše do daného souboru výsledky testování
	def solveAndSave(self, outputFilename):
		while self.canLearnMore():
			self.learnMore()
		outputFile = open(outputFilename, "w")
		for i in range(self.testingLen):
			outputFile.write(self.showTesting(i) + '\n')
		outputFile.close()
	

# třída grafu učících a testovaných bodů a přímky perceptronu
class Graph(gtk.DrawingArea):
	
	# provede zobrazení aktuálních informací
	def expose(self, widget, event):
		width, height = widget.window.get_size()
		self.cr = cr = widget.window.cairo_create()
		
		# celá plocha
		cr.set_source_rgb(1, 1, 1)
		cr.rectangle(0, 0, width, height)
		cr.fill()
		
		# plocha pro vykreslování grafu (bez legendy)
		self.width = width - 45
		self.height = height - 25
		
		self.drawGrid()
		self.drawLine()
		for i in range(self.app.maxLearn):  # vykreslení učících bodů
			self.drawPoint(self.app.net.learning[i])
		for i in range(self.app.maxTest):  # vykreslení testovaných bodů
			point = list()
			point.extend(self.app.net.testing[i])
			point.append(self.app.net.evaluate(self.app.net.testing[i]))
			self.drawPoint(point, True)
	
	# vykreslí mřížku grafu včetně legendy
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
	
	# převede souřadnice bodu na přípustné souřadnice uvnitř grafu
	def coordsNetToGraph(self, netX, netY):
		width = self.width; height = self.height
		x = netX * width
		y = netY * height
		return max(min(x, width), 0), max(min(y, height), 0)
	
	# vykreslí bod, ať již učící či testovaný (podle @testing)
	def drawPoint(self, point, testing = False):
		cr = self.cr; width = self.width; height = self.height
		
		x, y = self.coordsNetToGraph(point[0], point[1])
		radius = min(width, height) * 0.03
		color = [0, 1, 0] if point[2] == 1 else [1, 0, 0]
		
		cr.set_source_rgb(*color)
		cr.arc(x, y, radius, 0, 2 * pi)
		cr.fill()
		if testing:
			cr.set_source_rgb(0, 0, 0)
			cr.arc(x, y, radius / 3, 0, 2 * pi)
			cr.fill()
	
	# vykreslí přímku perceptronu
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


# třída GUI aplikace
class App(gtk.Window):
	
	maxLearn = 0  # maximální vykreslovaný učící bod
	maxTest = 0	  # maximální vykreslovaný testovaný bod
	
	# konstruktor, přijímá zpracovávanou síť a případně jméno vstupního souboru;
	# vytvoří GUI prvky okna a zobrazí jej
	def __init__(self, net, filename = ""):
		super(App, self).__init__()
		
		self.net = net
		
		s = " - " + filename if filename != "" else ""
		self.set_title("Simulace perceptronu neuronové sítě" + s)
		self.connect("delete-event", gtk.main_quit)
		self.set_border_width(5)
		
		vbox = gtk.VBox(False, 5)
		self.add(vbox)
		
		self.graph = graph = Graph()
		graph.app = self
		if self.net.inputsLen == 2:
			graph.connect("expose-event", graph.expose)
			graph.set_size_request(500, 500)
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
		
		self.textBuffer = gtk.TextBuffer()
		self.textArea = textArea = gtk.TextView()
		textArea.set_buffer(self.textBuffer)
		textArea.set_editable(False)
		textArea.set_cursor_visible(False)
		scrollArea = gtk.ScrolledWindow()
		scrollArea.add(textArea)
		scrollArea.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrollArea.set_size_request(500, 100)
		vbox.pack_start(scrollArea, True)
		
		self.show_all()
		self.printWeights()
	
	# vypíše text do textové oblasti a odřádkuje
	def printInArea(self, text):
		self.textBuffer.insert(self.textBuffer.get_end_iter(), text + '\n')
		self.textArea.scroll_to_iter(self.textBuffer.get_end_iter(), 0, \
			True, 0, 0)
	
	# vypíše do textové oblasti váhy vstupů perceptronu
	def printWeights(self):
		self.printInArea(self.net.showWeights())
	
	# obslouží zmáčknutí tlačítka pro další učení
	def nextLearning(self, widget):
		self.net.learnMore()
		self.printWeights()
		if self.maxLearn < self.net.learningLen:
			self.maxLearn += 1
		if not self.net.canLearnMore():
			self.nextLearningButton.set_sensitive(False)
			self.learnButton.set_sensitive(False)
		self.queue_draw()
	
	# obslouží zmáčknutí tlačítka pro kompletní naučení se
	def learn(self, widget):
		while self.net.canLearnMore():
			self.net.learnMore()
		self.printWeights()
		self.maxLearn = self.net.learningLen
		self.nextLearningButton.set_sensitive(False)
		self.learnButton.set_sensitive(False)
		self.queue_draw()
	
	# obslouží zmáčknutí tlačítka pro testování dalšího bodu
	def nextTesting(self, widget):
		self.printInArea(self.net.showTesting(self.maxTest))
		self.maxTest += 1
		if self.maxTest >= self.net.testingLen:
			self.nextTestingButton.set_sensitive(False)
		self.queue_draw()
	
	# obslouží zmáčknutí tlačítka pro reset
	def restart(self, widget):
		self.net.reset()
		self.maxLearn = self.maxTest = 0
		self.nextLearningButton.set_sensitive(True)
		self.learnButton.set_sensitive(True)
		self.nextTestingButton.set_sensitive(True)
		self.textBuffer.set_text("")
		self.printWeights()
		self.queue_draw()


# pokud je spuštěn přímo tento program, je proveden
if __name__ == "__main__":
	try:
		# načtení argumentů
		inputFilename = sys.argv[1]
		outputFilename = sys.argv[2] if len(sys.argv) > 2 else ""
	except:
		print "použití: " + sys.argv[0] + " VSTUPNÍ_SOUBOR [VÝSTUPNÍ_SOUBOR]"
		sys.exit(1)
	
	# incializace
	random.seed()

	inputNet = Net()
	inputNet.readInputFile(inputFilename)
	inputNet.reset()

	# v případě uvedení výstupního souboru se pouze provede výpočet,
	# který je následně uložen, jinak se spouští interaktivní GUI
	if outputFilename == "":
		App(inputNet, inputFilename)
		gtk.main()
	else:
		inputNet.solveAndSave(outputFilename)

