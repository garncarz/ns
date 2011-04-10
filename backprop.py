#!/usr/bin/python2
# -*- coding: utf-8 -*-

from backpropnet import *
from raceclient import *
import getopt, sys
import gtk

# třída argumentů programu
class Input:
	pass


class App(gtk.Window):

	def __init__(self):
		self.net = BackpropNet()  # vytvoření sítě
	
		super(App, self).__init__()
		self.set_title("Neuronová síť")
		self.connect("delete-event", gtk.main_quit)
		
		table = gtk.Table()
		self.add(table)
		table.set_row_spacings(5)
		table.set_col_spacings(5)
		
		self.textBuffer = gtk.TextBuffer()
		self.textArea = textArea = gtk.TextView()
		textArea.set_buffer(self.textBuffer)
		textArea.set_editable(False)
		textArea.set_cursor_visible(False)
		scrollArea = gtk.ScrolledWindow()
		scrollArea.add(textArea)
		scrollArea.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrollArea.set_size_request(500, 100)
		self.printInArea("Dobrý den, toto je informační plocha. " + \
			"Začněte načtením sítě.")
		table.attach(scrollArea, 0, 1, 0, 10)
		
		row = 0
		table.attach(gtk.Label("Vrstvy: "), 1, 2, row, row + 1)
		self.layersLabel = gtk.Label("0")
		table.attach(self.layersLabel, 2, 3, row, row + 1)
		self.layersButton = gtk.Button("Změnit")
		table.attach(self.layersButton, 3, 4, row, row + 1)
		
		row += 1
		table.attach(gtk.Label("Koeficient učení: "), 1, 2, row, row + 1)
		self.learningLabel = gtk.Label("0")
		table.attach(self.learningLabel, 2, 3, row, row + 1)
		self.learningButton = gtk.Button("Změnit")
		self.learningButton.connect("clicked", self.changeLearning)
		table.attach(self.learningButton, 3, 4, row, row + 1)
		
		row += 1
		table.attach(gtk.Label("Koeficient vlivu z předchozího kroku: "), 1, \
			2, row, row + 1)
		self.impactLabel = gtk.Label("0")
		table.attach(self.impactLabel, 2, 3, row, row + 1)
		self.impactButton = gtk.Button("Změnit")
		table.attach(self.impactButton, 3, 4, row, row + 1)
		
		row += 1
		self.loadInputButton = gtk.Button("Načíst síť")
		self.loadInputButton.connect("clicked", self.loadInput)
		table.attach(self.loadInputButton, 1, 4, row, row + 1)
		
		row += 1
		self.learnButton = gtk.Button("Naučit se síť")
		self.learnButton.connect("clicked", self.learn)
		table.attach(self.learnButton, 1, 4, row, row + 1)
		
		row += 1
		self.loadWeightsButton = gtk.Button("Načíst váhy")
		self.loadWeightsButton.connect("clicked", self.loadWeights)
		table.attach(self.loadWeightsButton, 1, 4, row, row + 1)
		
		row += 1
		self.saveWeightsButton = gtk.Button("Uložit váhy")
		self.saveWeightsButton.connect("clicked", self.saveWeights)
		table.attach(self.saveWeightsButton, 1, 4, row, row + 1)
		
		row += 1
		self.saveTestingButton = gtk.Button("Uložit vyhodnocenou trénovací " \
			+ "sadu")
		self.saveTestingButton.connect("clicked", self.saveTesting)
		table.attach(self.saveTestingButton, 1, 4, row, row + 1)
		
		row += 1
		self.testButton = gtk.Button("Dotaz")
		table.attach(self.testButton, 1, 4, row, row + 1)
		
		row += 1
		self.playButton = gtk.Button("Hrát závody")
		table.attach(self.playButton, 1, 4, row, row + 1)
		
		self.show_all()

	# vypíše text do textové oblasti a odřádkuje
	def printInArea(self, text):
		self.textBuffer.insert(self.textBuffer.get_end_iter(), text + '\n')
		self.textArea.scroll_to_iter(self.textBuffer.get_end_iter(), 0, \
			True, 0, 0)

	def changeLearning(self, weidget):
		dialog = gtk.MessageDialog( \
			parent = self, type = gtk.MESSAGE_QUESTION, \
			flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
			buttons = gtk.BUTTONS_OK, \
			message_format = "Nový koeficient učení:")
		entry = gtk.Entry()
		dialog.vbox.pack_end(entry, True, True, 0)
		dialog.show_all()
		dialog.run()

	def loadInput(self, widget):
		chooser = gtk.FileChooserDialog( \
			title = "Otevřít soubor sítě", parent = self, \
			action = gtk.FILE_CHOOSER_ACTION_OPEN, \
			buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
			gtk.STOCK_OK, gtk.RESPONSE_OK))
		if chooser.run() == gtk.RESPONSE_OK:
			try:
				self.net.readInputFile(chooser.get_filename())
				self.layersLabel.set_text(" ".join(map(lambda l: str(l), \
					self.net.layers[1:])))
				self.learningLabel.set_text(str(self.net.learning))
				self.impactLabel.set_text(str(self.net.impact))
				self.printInArea("Načtena síť z " + chooser.get_filename())
			except Exception as e:
				self.printInArea("Chyba: " + str(e))
		chooser.destroy()
	
	def learn(self, widget):
		try:
			self.printInArea("Začínám se učit... (postup možno sledovat na " + \
				"standardním výstupu)")
			self.net.learn()
			self.printInArea("Síť naučena. Výsledky testování:")
			self.printInArea(self.net.showAllTesting())
		except Exception as e:
			self.printInArea("Je načtena síť? Chyba: " + str(e))
	
	def loadWeights(self, widget):
		chooser = gtk.FileChooserDialog( \
			title = "Otevřít soubor s váhami", parent = self, \
			action = gtk.FILE_CHOOSER_ACTION_OPEN, \
			buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
			gtk.STOCK_OK, gtk.RESPONSE_OK))
		if chooser.run() == gtk.RESPONSE_OK:
			try:
				self.net.loadWeights(chooser.get_filename())
				self.printInArea("Načteny váhy z " + chooser.get_filename())
			except Exception as e:
				self.printInArea("Chyba: " + str(e))
		chooser.destroy()
	
	def saveWeights(self, widget):
		chooser = gtk.FileChooserDialog( \
			title = "Uložit váhy do souboru", parent = self, \
			action = gtk.FILE_CHOOSER_ACTION_SAVE, \
			buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
			gtk.STOCK_OK, gtk.RESPONSE_OK))
		if chooser.run() == gtk.RESPONSE_OK:
			try:
				self.net.saveWeights(chooser.get_filename())
				self.printInArea("Váhy uloženy do " + chooser.get_filename())
			except Exception as e:
				self.printInArea("Chyba: " + str(e))
		chooser.destroy()
	
	def saveTesting(self, widget):
		chooser = gtk.FileChooserDialog( \
			title = "Uložit výsledky do souboru", parent = self, \
			action = gtk.FILE_CHOOSER_ACTION_SAVE, \
			buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
			gtk.STOCK_OK, gtk.RESPONSE_OK))
		if chooser.run() == gtk.RESPONSE_OK:
			try:
				self.net.saveTesting(chooser.get_filename())
				self.printInArea("Výsledky uloženy do " + \
					chooser.get_filename())
			except Exception as e:
				self.printInArea("Chyba: " + str(e))
		chooser.destroy()

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
			client.run()  # samotná hra
			client.close()  # odpojení
	except Exception as e:  # někde nastala chyba
		print "Error: " + str(e)


# pokud je spuštěn přímo tento program, je proveden
if __name__ == "__main__":
	# main()
	App()
	gtk.main()

