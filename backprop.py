#!/usr/bin/python2
# -*- coding: utf-8 -*-

import math
import random


class Net:

	# váhy[vrstva][odkud][kam]
	weight = list()
	# hodnoty předávané neurony[vrstva][odkud][kam]
	x = list()
	kurtosis = list()
	lastChange = list()
	

	def __init__(self, layers, inputs, outputs, learning, impact):
		layers[0] += 1
		
		for layer in range(len(layers)):
			self.weight[layer] = list()
			self.x[layer] = list()
			self.kurtosis[layer] = list()
			self.lastChange[layer] = list()
		
		for layer in range(len(layers)):
			for src in range(layers[layer]):
				self.kurtosis[layer][src] = 0.5
				self.weight[layer][src] = list()
				for to in range(layers[layer + 1]):
					self.weight[layer][src][to] = random.random()
		# self.x[0][layers[0] - 1] = 1
	
	def evaluate(self, inputs):
		self.x[0] = inputs + [1]

		for layer in range(len(self.weight) - 1):
			for to in range(len(self.weight[layer + 1])):
				z = 0.0
				for src in range(len(self.weight[layer])):
					z += self.weight[layer][src][to] * self.x[layer][src]
				self.x[layer + 1][to] = 1 / (1 + \
					math.exp(-self.kurtosis[layer + 1][to] * z))
		
		return self.x[len(self.x) - 1]

	def backPropagate(self, goals):
		
		
