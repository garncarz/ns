#!/usr/bin/python2
# -*- coding: utf-8 -*-

from backpropnet import *
from PIL import Image

def process(country, width, height):
	net = BackpropNet()
	net.readInputFile("flag." + country)
	net.loadWeights("flag." + country + ".weights")
	img = Image.new("RGB", (width, height))
	for x in range(width):
		for y in range(height):
			c = net.evaluate([float(x) / width, float(y) / height])
			c = map(lambda perc: int(perc * 255), c)
			img.putpixel((x, y), (c[0], c[1], c[2]))
	img.save("flag." + country + ".png")

process("cz", 300, 200)
process("de", 500, 300)

