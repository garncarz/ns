#!/usr/bin/python2
# -*- coding: utf-8 -*-

import math
import random

class Neuron:
	
	inputNeurons = list()
	inputWeights = list()
	inputs = list()
	remainingInputs = 0
	outputNeurons = list()
	
	def __init(self, kurtosis = 0.5):
		self.kurtosis = kurtosis
	
	def addInputNeuron(self, inp):
		self.inputNeurons.append(inp)
		self.inputWeights.append(random.random())
		self.inputs.append(-1)
		self.remainingInputs += 1
	
	def addOutputNeuron(self, out):
		self.outputNeurons.append(out)
	
	def compute(self):
		z = 0
		for i, x in self.inputs:
			z += self.inputWeights[i] * x
		y = 1 / (1 + math.exp(-self.kurtosis * z))
		for o in self.outputNeurons:
			o.setInput(self, y)
			print y
	
	def setInput(self, neuron, value):
		pos = self.inputNeurons.index(neuron)
		if self.inputs[pos] == -1:
			if self.remainingInputs == 0:
				self.remainingInputs = len(self.inputNeurons) - 1
				for i in range(self.inputs):
					self.inputs[i] = -1
			else:
				self.remainingInputs -= 1
		self.inputs[pos] = value
		if self.remainingInputs == 0:
			self.compute()


class Input:
	
	name = ""
	minVal = 0.0
	maxVal = 1.0
	outputNeurons = list()
	
	def __init__(self, name, minVal, maxVal):
		self.name = name
		self.minVal = minVal
		self.maxVal = maxVal
	
	def addOutputNeuron(self, out):
		self.outputNeurons.append(out)


class Output:
	
	name = ""
	inputNeurons = list()
	
	def __init__(self, name):
		self.name = name
	
	def addInputNeuron(self, inp):
		self.inputNeurons.append(inp)
	
	def setInput(self, neuron, value):
		self.value = value


class BackpropNet:

	neurons = list()
	inputs = list()
	outputs = list()

	def __init__(self, layers, inputs, outputs, learning, impact):
		# vytvoření neuronů
		for i in range(len(layers)):
			self.neurons.append(list())
			for j in range(layers[i]):
				self.neurons[i].append(Neuron())
	
		# propojení neuronů
		for i in range(len(layers) - 1):
			for j in range(len(self.neurons[i])):
				for k in range(len(self.neurons[i + 1])):
					self.neurons[i][j].addOutputNeuron(self.neurons[i + 1][k])
					self.neurons[i + 1][k].addInputNeuron(self.neurons[i][j])
		
		# vytvoření vstupů a jejich propojení s nultou řadou neuronů
		for i in inputs:
			inp = Input(*i)
			self.inputs.append(inp)
			for n in self.neurons[0]:
				inp.addOutputNeuron(n)
		
		# vytvoření výstupu a jeho propojení s poslední řadou neuronů
		for o in range(len(outputs)):
			out = Output(outputs[o])
			self.outputs.append(out)
			self.neurons[len(self.neurons) - 1][o].addOutputNeuron(out)
			out.addInputNeuron(self.neurons[len(self.neurons) - 1][o])
			
		

b = BackpropNet([2, 3], [["input", 2, 3]], ["output"], 1, 1)


