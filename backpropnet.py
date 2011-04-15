#!/usr/bin/python2
# -*- coding: utf-8 -*-

import math
import random

# maximální přístupná chyba
maxError = 0.2

# třída neuronové sítě
class BackpropNet:

	# váhy[vrstva kam][neuron kam][neuron odkud]
	weight = list()
	# hodnoty vygenerované neurony[vrstva][neuron], nultá řada jsou vstupy
	y = list()
	# strmost sigmoidu[vrstva][neuron]
	kurtosis = list()
	# rozdíl mezi skutečnou a požadovanou odezvou[vrstva][neuron]
	delta = list()
	# poslední změna[vrstva][neuron]
	lastChange = list()
	
	# koeficient učení
	learning = 0.4
	# koeficient vlivu předchozí změny
	impact = 0.2
	
	# inicializace proměnných třídy po načtení vstupních údajů
	def init(self):
		# vymazání od minulého nastavení:
		self.weight = list()
		self.y = list()
		self.kurtosis = list()
		self.delta = list()
		self.lastChange = list()
		
		# vytvoření struktury:
		for layer in range(self.layersLen):
			self.y.append([0.0] * self.layers[layer])
			self.kurtosis.append([0.5] * self.layers[layer])
			self.delta.append([0.0] * self.layers[layer])
			self.lastChange.append([0.0] * self.layers[layer])
			self.weight.append(list())
			for to in range(self.layers[layer]):
				self.weight[layer].append(list())
				for src in range(self.layers[layer - 1]):
					self.weight[layer][to].append(random.uniform(-1, 1))
					#self.weight[layer][to].append(random.uniform(0, 0.2))
		
		# aktuální prvek trénovací množiny
		self.toLearn = 0
		
		# počet proběhlých učení
		self.history = 0

	############################################################################
	# stěžejní funkce:

	# vyhodnotí daný vstup
	def evaluate(self, inputs):
		# poslední neuron nulté řady je přídavný "nabuzený"
		self.y[0] = inputs[:self.inputsLen] + [1.0]

		for layer in range(1, self.layersLen):
			for to in range(len(self.weight[layer])):
				z = 0.0
				for src in range(len(self.weight[layer - 1])):
					z += self.weight[layer][to][src] * self.y[layer - 1][src]
				self.y[layer][to] = 1.0 / (1.0 + \
					math.exp(-self.kurtosis[layer][to] * z))
		
		return self.y[self.layersLen - 1]

	# pokusí se vylepšit váhy mezi neurony podle očekávaného výstupu
	def backPropagate(self, goals):
		# spočtení delt, vrstvy jdou pozpátku:
		layer = self.layersLen - 1  # u poslední vrstvy se počítá jinak
		for src in range(len(self.y[layer])):
			self.delta[layer][src] = self.y[layer][src] - goals[src]
		for layer in range(layer - 1, 0, -1):
			for src in range(len(self.y[layer])):
				self.delta[layer][src] = 0
				for to in range(len(self.y[layer + 1])):
					self.delta[layer][src] += self.delta[layer + 1][to] * \
						self.y[layer + 1][to] * (1.0 - self.y[layer + 1][to]) \
						* self.kurtosis[layer][src] * \
						self.weight[layer + 1][to][src]
		
		# změny vah:
		for layer in range(1, self.layersLen):
			for to in range(len(self.y[layer])):
				for src in range(len(self.y[layer - 1])):
					gradient = self.delta[layer][to] * self.y[layer][to] * \
						(1.0 - self.y[layer][to]) * self.kurtosis[layer][to] * \
						self.y[layer - 1][src]
					self.weight[layer][to][src] -= self.learning * gradient + \
						self.impact * self.lastChange[layer][to]
					self.lastChange[layer][to] = gradient

	############################################################################
	# učení a testování:
	
	# vrátí celkovou chybu pro trénovací množinu
	def error(self):
		error = 0.0
		for i in range(self.learningLen):
			error += sum(map(lambda (y, o): (y - o) ** 2, \
				zip(self.evaluate(self.learningElem[i]), \
				self.learningElem[i][self.inputsLen:])))
		return error / 2.0
	
	# postoupí ve fázi učení
	def learnMore(self):
		self.evaluate(self.learningElem[self.toLearn])
		self.backPropagate(self.learningElem[self.toLearn][self.inputsLen:])
		self.toLearn += 1  # další bod k učení
		if self.toLearn == self.learningLen: self.toLearn = 0
		if self.history % 1000 == 0:
			print str(self.history / 1000) + 'k', self.error()
		self.history += 1
	
	# vrátí, zda-li je možné se ještě něco naučit
	def canLearnMore(self):
		global maxError
		# budeme kontrolovat nepotřebnost učení jen po určitém počtu kroků
		# - pro urychlení
		if self.history % 1000 == 0:
			return False if self.error() < maxError else True
		return True
	
	# naučí se síť
	def learn(self):
		while self.canLearnMore():
			self.learnMore()
	
	############################################################################
	# řešení a výstup:
	
	# vrátí řetězec výsledku testování daného vstupu
	def showTesting(self, nr):
		return "".join(map(lambda x: x + ' ', self.testingOrig[nr])) + \
			"".join(map(lambda y: str(y) + ' ', \
			self.evaluate(self.testingElem[nr])))
	
	# vrátí řetězec s výsledky všech testů
	def showAllTesting(self):
		out = ""
		for i in range(self.testingLen):
			out += self.showTesting(i) + '\n'
		return out
	
	# vypíše do daného souboru výsledky testování
	def saveTesting(self, outputFilename):
		outputFile = open(outputFilename, "w")
		outputFile.write(self.showAllTesting())
		outputFile.close()
	
	# vrátí řetězec s váhami
	def showWeights(self):
		return '|'.join( \
			map(lambda layer: ';'.join( \
				map(lambda to: ','.join( \
					map(lambda src: str(src), to)), layer)), \
			self.weight))
	
	# uloží váhy do daného souboru
	def saveWeights(self, filename):
		outputFile = open(filename, "w")
		outputFile.write(self.showWeights())
		outputFile.close()

	############################################################################
	# načítání dat:

	# třída vstupu sítě
	class Input:
	
		# konstruktor, přiřadí vlastnostem vstupu přijaté hodnoty
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				setattr(self, key, value)
		
		# vrátí rozsah hodnot daného vstupu
		def rangeVal(self):
			return self.maxVal - self.minVal

	# načte informace popisující a testující síť z daného souboru
	def readInputFile(self, inputFilename):
	 
	 	# vrátí následující informativní řádku souboru
		def readLine():
			line = ""
			while line == "" or line.startswith('#'):
				line = inputFile.readline().lstrip()
			return line

		inputFile = open(inputFilename, "r")

		# počet vrstev, + 1 kvůli extra vrstvě pro vstup
		self.layersLen = int(readLine()) + 1

		# vstupy:
		self.inputsLen = int(readLine())  # počet vstupů
		self.inputs = list()
		for i in range(self.inputsLen):
			name, minVal, maxVal = readLine().split()
			self.inputs.append(self.Input(name = name,
				minVal = float(minVal), maxVal = float(maxVal)))
		self.inputs.append(self.Input(name = "nulák",  # poslední je fixní
			minVal = 0.0, maxVal = 1.0))  # s nasyceným příjmem
			
		# vrstvy, nultá je přidná vrstva pro vstupy
		#self.layers = [self.inputsLen] + \
		self.layers = [self.inputsLen + 1] + \
			map(lambda l: int(l), readLine().split())
		
		# výstupy:
		for i in range(self.layers[self.layersLen - 1]):
			readLine()  # nepotřebujeme jejich názvy

		self.learning = float(readLine())  # koeficient učení
		
		self.impact = float(readLine())  # koeficient vlivu předchozí změny

		# trénovací body:
		self.learningLen = int(readLine())  # počet
		self.learningElem = list()
		for i in range(self.learningLen):
			self.learningElem.append(self.normalizeValues(readLine().split()))

		# testovací body:
		self.testingLen = int(readLine())  # počet
		self.testingOrig = list()  # originální zadání
		self.testingElem = list()  # normalizované hodnoty
		for i in range(self.testingLen):
			line = readLine().split()
			self.testingOrig.append(line)
			self.testingElem.append(self.normalizeValues(line))

		inputFile.close()
		
		# inicializace dalších proměnných třídy podle již načtených údajů
		self.init()
	
	# vrátí normalizované hodnoty vstupu pro rozsah <0, 1>
	def normalizeValues(self, values):
		newValues = list()
		for i in range(self.inputsLen):
			newValues.append((float(values[i]) - self.inputs[i].minVal) \
				/ self.inputs[i].rangeVal())
		for i in range(self.inputsLen, len(values)):
			newValues.append(float(values[i]))
		return newValues
	
	# načte váhy z daného souboru
	def loadWeights(self, filename):
		inputFile = open(filename, "r")
		content = inputFile.readline()
		self.weight = map(lambda layer: \
			map(lambda to: \
				map(lambda src: float(src), to.split(',')), \
				layer.split(';')), \
			content.split('|'))
		inputFile.close()
	
	# nastaví vrstvy
	def setLayers(self, layersString):
		self.layers = [self.inputsLen + 1] + \
			map(lambda l: int(l), layersString.split())
		self.layersLen = len(self.layers)
		self.init()  # nutná reinicializace


