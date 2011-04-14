#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Vícevrstvá neuronová síť s metodou učení backpropagation
# Autor: Ondřej Garncarz, 2011
# Program je napsán v jazyce Python (verze 2.7) a využívá prostředí GTK.
# Obsluha je plně v rámci GUI.

from backpropnet import *
from raceclient import *
import gtk, gtk.glade, gtk.gdk


# třída GUI aplikace
class App(gtk.Window):

	# inicializace okna a napojené sítě a herního klienta
	def __init__(self):
		self.net = BackpropNet()  # vytvoření sítě
		self.raceClient = RaceClient()  # klient pro hru aut
	
		super(App, self).__init__()
		self.set_title("Neuronová síť")
		self.connect("delete-event", gtk.main_quit)
		
		# šablona pro určité dialogové GUI prvky
		self.glade = gtk.glade.XML("gui.glade")
		
		# tabulkové rozložení hlavního okna
		table = gtk.Table()
		self.add(table)
		table.set_row_spacings(5)
		table.set_col_spacings(5)
		
		# informační plocha
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
		
		# tabulka:
		
		# určité hodnoty sítě včetně možnosti změny:
		row = 0
		table.attach(gtk.Label("Vrstvy: "), 1, 2, row, row + 1)
		self.layersLabel = gtk.Label("0")
		table.attach(self.layersLabel, 2, 3, row, row + 1)
		self.layersButton = gtk.Button("Změnit")
		self.layersButton.set_sensitive(False)
		self.layersButton.connect("clicked", self.changeLayers)
		table.attach(self.layersButton, 3, 4, row, row + 1)
		
		row += 1
		table.attach(gtk.Label("Koeficient učení: "), 1, 2, row, row + 1)
		self.learningLabel = gtk.Label(self.net.learning)
		table.attach(self.learningLabel, 2, 3, row, row + 1)
		self.learningButton = gtk.Button("Změnit")
		self.learningButton.connect("clicked", self.changeLearning)
		table.attach(self.learningButton, 3, 4, row, row + 1)
		
		row += 1
		table.attach(gtk.Label("Koeficient vlivu z předchozího kroku: "), 1, \
			2, row, row + 1)
		self.impactLabel = gtk.Label(self.net.impact)
		table.attach(self.impactLabel, 2, 3, row, row + 1)
		self.impactButton = gtk.Button("Změnit")
		self.impactButton.connect("clicked", self.changeImpact)
		table.attach(self.impactButton, 3, 4, row, row + 1)
		
		# operace se sítí:
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
		
		# operace se vstupy:
		row += 1
		self.saveTestingButton = gtk.Button("Uložit vyhodnocenou trénovací " \
			+ "sadu")
		self.saveTestingButton.connect("clicked", self.saveTesting)
		table.attach(self.saveTestingButton, 1, 4, row, row + 1)
		
		row += 1
		self.queryButton = gtk.Button("Dotaz")
		self.queryButton.connect("clicked", self.query)
		table.attach(self.queryButton, 1, 4, row, row + 1)
		
		# tlačítko pro hru aut
		row += 1
		self.gameButton = gtk.Button("Hrát závody")
		self.gameButton.connect("clicked", self.game)
		table.attach(self.gameButton, 1, 4, row, row + 1)
		
		# zobrazení okna
		self.show_all()

	# vypíše text do textové oblasti a odřádkuje
	def printInArea(self, text):
		self.textBuffer.insert(self.textBuffer.get_end_iter(), text + '\n')
		self.textArea.scroll_to_iter(self.textBuffer.get_end_iter(), 0, \
			True, 0, 0)

	# změna topologie sítě
	def changeLayers(self, widget):
		dialog = self.glade.get_widget("layersDialog")
		self.glade.get_widget("layersNewValue").set_text(" ".join \
			(map(lambda l: str(l), self.net.layers[1:])))
		if dialog.run() == 1:
			try:
				self.net.setLayers(self.glade.get_widget("layersNewValue") \
					.get_text())
			except Exception as e:
				self.printInArea("Chyba: " + str(e))
			self.layersLabel.set_text(" ".join(map(lambda l: str(l), \
				self.net.layers[1:])))
		dialog.hide()

	# změna koeficientu učení
	def changeLearning(self, weidget):
		dialog = self.glade.get_widget("learningDialog")
		self.glade.get_widget("learningNewValue").set_text \
			(str(self.net.learning))
		if dialog.run() == 1:
			self.net.learning = float(self.glade.get_widget \
				("learningNewValue").get_text())
			self.learningLabel.set_text(str(self.net.learning))
		dialog.hide()
	
	# změnu vlivu z poslední změny
	def changeImpact(self, widget):
		dialog = self.glade.get_widget("impactDialog")
		self.glade.get_widget("impactNewValue").set_text(str(self.net.impact))
		if dialog.run() == 1:
			self.net.impact = float(self.glade.get_widget("impactNewValue") \
				.get_text())
			self.impactLabel.set_text(str(self.net.impact))
		dialog.hide()

	# načtení sítě
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
				self.layersButton.set_sensitive(True)
				self.learningLabel.set_text(str(self.net.learning))
				self.impactLabel.set_text(str(self.net.impact))
				self.printInArea("Načtena síť z " + chooser.get_filename())
			except Exception as e:
				self.printInArea("Chyba: " + str(e))
		chooser.destroy()
	
	# síť se naučí podle načtených dat
	def learn(self, widget):
		try:
			self.printInArea("Začínám se učit... (postup možno sledovat na " + \
				"standardním výstupu)")
			self.net.learn()
			self.printInArea("Síť naučena. Výsledky testování:")
			self.printInArea(self.net.showAllTesting())
		except Exception as e:
			self.printInArea("Je načtena síť? Chyba: " + str(e))
	
	# načtení vah ze souboru
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
	
	# uložení vah do souboru
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
	
	# otestování testovací sady a uložení výsledků
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
	
	# vlastní dotaz na síť
	def query(self, widget):
		dialog = self.glade.get_widget("queryDialog")
		if dialog.run() == 1:
			try:
				self.printInArea("Výsledek dotazu: " + \
					" ".join(map(lambda o: str(o), \
						self.net.evaluate(map(lambda i: int(i), \
							self.glade.get_widget("queryValue") \
								.get_text().split())))))
			except Exception as e:
				self.printInArea("Je naučena síť? Je správný počet vstupů? " + \
					"Chyba: " + str(e))
		dialog.hide()
	
	# hra aut
	def game(self, widget):
		dialog = self.glade.get_widget("gameDialog")
		self.glade.get_widget("gameServer").set_text(str( \
			self.raceClient.server))
		self.glade.get_widget("gamePort").set_text(str(self.raceClient.port))
		self.glade.get_widget("gameRace").set_text(str(self.raceClient.race))
		self.glade.get_widget("gameDriver").set_text(str( \
			self.raceClient.driver))
		self.glade.get_widget("gameColor").set_current_color(gtk.gdk.color_parse( \
			"#" + self.raceClient.color))
		if dialog.run() == 1:
			dialog.hide()
			self.raceClient.server = self.glade.get_widget("gameServer") \
				.get_text()
			self.raceClient.port = self.glade.get_widget("gamePort").get_text()
			self.raceClient.race = self.glade.get_widget("gameRace").get_text()
			self.raceClient.driver = self.glade.get_widget("gameDriver") \
				.get_text()
			c = self.glade.get_widget("gameColor") \
				.get_current_color().to_string()[1:]
			self.raceClient.color = c[0:2] + c[4:6] + c[8:10]
			self.raceClient.net = self.net
			try:
				self.printInArea("Připojuji se...")
				self.raceClient.connect()
				self.printInArea("Začínám hrát...")
				self.raceClient.run()
				self.printInArea("Hra skončila.")
				self.raceClient.close()
			except Exception as e:
				self.printInArea("Chyba: " + str(e))
		dialog.hide()


# pokud je spuštěn přímo tento program, je proveden
if __name__ == "__main__":
	App()
	gtk.main()

