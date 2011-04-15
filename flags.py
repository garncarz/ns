#!/usr/bin/python2
# -*- coding: utf-8 -*-

from backpropnet import *
from PIL import Image

# třída pro vytvoření výukových dat pro vlajku či její zhotovení z již naučené
# sítě
class Flag:

	# vytvoří soubor s definicí sítě a výukovými daty pro daný stát
	def createLearningFile(self, country):
		img = Image.open("orig." + country + ".png")
		netFile = open("flag." + country, "w")
		netFile.write("4\n2\nx 0 1\ny 0 1\n6 5 4 3\nr\ng\nb\n0.4\n0.1\n")
		(width, height) = img.size
		netFile.write(str(width * height) + '\n')
		for x in range(width):
			for y in range(height):
				netFile.write(str(float(x) / width) + ' ' + \
					str(float(y) / height) + ' ' + ' '.join(map( \
					lambda col: str(col / 255.0), img.getpixel((x, y))[:-1])) \
					+ '\n')
		netFile.write("0\n")
		netFile.close()
	
	# zhotoví vlajku pro daný stát o daných rozměrech
	def process(self, country, width, height):
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


# ukázková funkce
def demo():
	Flag().process("cz", 300, 200)
	Flag().process("de", 500, 300)
	Flag().process("il", 110, 80)

if __name__ == "__main__":
	demo()

