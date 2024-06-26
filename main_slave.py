from machine import Pin, Timer
import time
import network
from umqtt.robust import MQTTClient
import ujson
from simonsays import SimonSays
from morse import Morse
from matricna import MatricnaGame
from potenciometar import Potenciometar
from button import Button
from wirecutter import WireCutter

#___________________________________Glob varijable______________________________________________#
main_ready = False
state = 0
run = False
#___________________________________Pinouts_____________________________________________________#

simon_buttons = [8, 9, 10]
simon_leds = [11, 12, 13]
pins_izlazna = [0, 1, 2, 3] # za matricnu tastaturu
pins_ulazna = [4, 5, 6, 7] # mislim da su ovo redovi po sjecanju
pin_potenciometar = [28]
morse_pins = [14, 27] # jedna ledica za morse kod prikaz i ulaz signala
button_game_pins = [15] # jedno dugme, button zauzima vec ss=16, sck=18, mosi=19!
wire_pins = [17, 20, 21, 22, 26] # sta god ali 5
#___________________________________Pomocne funkcije____________________________________________#
topics = [b'katane/main_ready', b'katane/game_state', b'katane/game_over']
def subscribe(topic, msg):
	global run, main_ready, state, main_timer, spammer
	if topic == b'katane/main_ready' and msg == b'1':
		main_ready = True
		spammer.deinit()
	if topic == b'katane/game_state':
		parsed = ujson.loads(msg)
		state = int(parsed["state"])
		run = True
	if topic == b'katane/game_over' and msg in (b'win', b'lose'):
		main_timer.deinit()
		run = False

def check(t):
	global moduli_pool, strikes, solved, solved_moduli
	
	new_strikes = 0
	new_pool = []

	for m in solved_moduli:
		new_strikes += m.get_strikes()

	for m in moduli_pool:
		new_strikes += m.get_strikes()
		if m.solved:
			solved_moduli.append(m)
		else:
			new_pool.append(m)

	moduli_pool = new_pool

	if new_strikes != strikes:
		strikes = new_strikes
		mqtt_conn.publish(b'katane/slave_strike', str(strikes).encode('ascii'))
	if solved != len(solved_moduli):
		solved = len(solved_moduli)
		mqtt_conn.publish(b'katane/slave_solved', str(solved).encode('ascii'))

def spam(t):
	mqtt_conn.publish(b'katane/slave_present', b'1')
	print('main ziv sam!!!')
#___________________________________Spajanje na Wifi____________________________________________#

network_name = 'Wifi'
network_password = 'password'

nic = network.WLAN(network.STA_IF)
nic.activate(True)
nic.connect(network_name, network_password)

while not nic.isconnected():
    print('Cekam vezu')
    time.sleep(1)

#___________________________________Game setup____________________________________________#
broker='192.168.100.10'
mqtt_conn = MQTTClient(client_id='slavepico', server='broker.emqx.io',user='',password='',port=1883, keepalive=300)
mqtt_conn.set_callback(subscribe)
mqtt_conn.connect()
for t in topics:
	mqtt_conn.subscribe(t)

spammer = Timer(period=100, mode=Timer.PERIODIC, callback=spam)

while not main_ready:
	mqtt_conn.publish(b'katane/slave_present', b'1')
	print('cekam main da se javi da je ziv')
	mqtt_conn.wait_msg()

while not run:
	print('cekam informacije o igri...')
	mqtt_conn.wait_msg()

moduli_pool = [SimonSays(state, simon_buttons, simon_leds),
				MatricnaGame(state, pins_izlazna, pins_ulazna),
				Potenciometar(state, pin_potenciometar),
				Morse(state, morse_pins),
				Button(state, button_game_pins),
				WireCutter(wire_pins, wire_pins, state)]

solved_moduli = []

main_timer = Timer(period=500, mode=Timer.PERIODIC, callback=check)


while run:
	print('game is running...')
	time.sleep(1)

print('Game over!')
for m in moduli_pool:
	m.deinit()
for m in solved_moduli:
	m.deinit()
mqtt_conn.disconnect()