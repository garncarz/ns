#!/usr/bin/python2
# -*- coding: utf-8 -*-

from backpropnet import *
from raceclient import *
import getopt, sys

# třída argumentů programu
class Input:
	pass

# hlavní funkce běhu programu
def main():
	# načtení vstupu:
	try:
		opts, args = getopt.getopt(sys.argv[1:], "", [ \
			"loadW", "genOut", "play", \
			"input=", "output=", "weights=", \
			"server=", "port=", "race=", "driver=", "color="])
	except getopt.GetoptError:
		sys.exit(1)
	inp = Input()
	for o, v in opts:
		setattr(inp, o[2:], v)
	
	# akce podle parametrů:
	try:
		net = BackpropNet()  # vytvoření sítě
		net.readInputFile(inp.input)
		
		if hasattr(inp, "loadW"):  # načtení vah
			net.loadWeights(inp.weights)
		
		if hasattr(inp, "genOut"):  # naučení se podle vstupu a uložení
			net.solveAndSave(inp.output)
			net.saveWeights(inp.weights)  # uložení i vah
		
		if hasattr(inp, "play"):  # závodní hra
			client = RaceClient(net)
			for atr in ["server", "port", "race", "driver", "color"]:
				if hasattr(inp, atr):  # parametry připojení a hry
					setattr(client, atr, getattr(inp, atr))
			client.connect()  # připojení k serveru
			client.play()  # samotná hra
			client.close()  # odpojení
	except Exception as e:  # někde nastala chyba
		print "Error: " + str(e)


# pokud je spuštěn přímo tento program, je proveden
if __name__ == "__main__":
	main()

