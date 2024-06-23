from machine import Pin
import time
import network
from umqtt.robust import MQTTClient
import ujson
from simonsays import SimonSays
from morse import Morse
from matricna import MatricnaGame
from potenciometar import Potenciometar
from button import Button
from wires import Wires
# Raspberry master

# spoji se na internet
import network
import time
from machine import Pin
from umqtt.robust import MQTTClient
import ujson


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
def subscribe(topic, msg):
	global run, main_ready, state, main_timer
	if topic == b'katane/main_ready' and msg == b'1':
		main_ready = True
	if topic == b'katane/game_state':
		parsed = ujson.loads(msg)
		state = int(parsed["state"])
		run = True
	if topic == b'katane/game_over' and msg in (b'win', b'lose'):
		main_timer.deinit()
		run = False

def check(t):
	global moduli_pool, strikes, solved
	strikes = 0
	new_pool = []
	for m in moduli_pool:
		if not m.solved:
			new_pool.append(m)
		else:
			solved += 1
		strikes += m.get_strikes()
	moduli_pool = new_pool
	mqtt_conn.publish(b'katane/slave_strike', str(strikes).encode('ascii'))
	if solved != 0:
		mqtt_conn.publish(b'katane/slave_solved', str(solved).encode('ascii'))
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
mqtt_conn = MQTTClient(client_id='slavepico', server='broker.hivemq.com',user='',password='',port=1883)
mqtt_conn.set_callback(subscribe)
mqtt_conn.connect()
mqtt_conn.subscribe(b"katane/#")

while not main_ready:
	mqtt_conn.wait_msg()

while not run:
	mqtt_conn.wait_msg()

moduli_pool = [SimonSays(state, simon_buttons, simon_leds),
				MatricnaGame(state, pins_izlazna, pins_ulazna),
				Potenciometar(state, pin_potenciometar),
				Morse(state, morse_pins),
				Button(state, button_game_pins),
				Wires(state, wire_pins)]

main_timer = Timer(period=100, mode=Timer.PERIODIC, callback=check)


while run:
	print('game is running...')
	time.sleep(1)