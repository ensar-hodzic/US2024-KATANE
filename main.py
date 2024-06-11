from machine import Pin
import time
import network
from umqtt.robust import MQTTClient
import ujson
from labirint import *
from decode import *
from simon_says import * # NE POSTOJI TRENUTNO JEL!!!!!


class MainKatane:
	labirint_pins = [] # lista pinova za labirint
	display_pins = [] # lista pinova za display decode modula
	rotacioni_pins = [] # lista pinova za rotacioni enkoder decode modula
	simon_led_pins = [] # lista pinova za 3 ledice simon says modula
	simon_button_pins = [] # lista pinova za 3 tastera simon says modula

	rgb_pins = [] #pinovi rgba

	def __init__(self, state, mqtt_conn):
		self.mqtt = mqtt_conn
		self.mqtt = MQTTClient(clientid='master', server='broker.hivemq.com', user='', password='', port=1883)
		self.mqtt.set_callback(self.subscription)
		self.mqtt.connect()


		moduli=[b"katane/morse", b"katane/simon_says", b"katane/button_press", b"katane/wires", b"katane/password"]# lista modula na slaveu
		mqtt_conn.subscribe(moduli)
		self.countdown = Timer(-1)
		self.main_timer = Timer(-1)

		self.strikes = state % 4 # dozvoljene greske
		self.simons_word = self.generate_simon_word(state)

		self.display_rgb_state(state)

		self.solved_count_local = 0 # koliko je main izbrojao 
		self.solved_count_slave = 0 # koliko je slave izbrojao


	def main(self, t):
		self.solved_count_local = 0
		for modul in moduli:
			self.solved_count_local += modul.solved

		if self.solved_count_slave + self.solved_count_local == 7:
			# igra rjesena
			self.countdown.deinit() # prestani countdown
			self.main_timer.deinit()
			self.mqtt.publish(b'katane/game_over', b'win')

		if self.strikes < 0:
			self.explode(t)


	def run(self):
		# okini module
		self.moduli = [Labirint(self.labirint_pins), 
			DecodeModul(self.display_pins, self.rotacioni_pins), #BANDA NAPRAVI OVO DA ZNM STA COVJEKU SLAT
			SimonSays(self.simons_word , self.simon_led_pins, self.simon_button_pins)]

		self.publish_labirint_path()

		self.main_timer.init(mode=Timer.PERIODIC, callback=self.main)
		self.countdown.init(mode=Timer.ONE_SHOT, callback=self.explode)

	def subscription(self, topic, msg):
		if topic == b'katane/main_inbox/modul_solved':
			self.solved_count_slave = int(msg)
		if topic == b'katane/game_)start' and msg == b'1':
			self.run()
		if topic == b'katane/strike':
			self.strikes -= 1


	def explode(self, t):
		self.mqtt.publish(b'katane/main_inbox/game_over', b'lose')
		self.main_timer.deinit() 

	def publish_labirint_path(self):
		l = self.moduli[0].get_path()
		json_str = json.dumps(l)
		self.mqtt.publish(b'katane/main_inbox/labirint_path', json_str.encode('ascii'))


	@staticmethod
	def generate_simon_word(state):
		#banda napravi ovo

	def display_rgb_state(self, state):
		r = Pin(self.rgb_pins[0])
		g = Pin(self.rgb_pins[1])
		b = Pin(self.rgb_pins[2])

		r.value(state & 100)
		b.value(state & 010)
		g.value(state & 001)

