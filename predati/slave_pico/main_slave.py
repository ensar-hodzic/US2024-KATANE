from machine import Pin, Timer
import time
import network
from umqtt.robust import MQTTClient
import ujson
from simonsays import SimonSays
from matricna import MatricnaGame
from button import Button


#___________________________________Glob varijable______________________________________________#
main_ready = False
state = 0
strikes = 0
solved = 0
run = False
main_timer = Timer(-1)
network_name = "IME_MREZE"
network_password = 'SIFRA_MREZE'
SERVER='192.168.43.69' # mqtt broker
#___________________________________Pinouts_____________________________________________________#

simon_buttons = [8, 9, 10]
simon_leds = [11, 12, 13]
pins_izlazna = [0, 1, 2, 3] # za matricnu tastaturu
pins_ulazna = [4, 5, 6, 7] # mislim da su ovo redovi po sjecanju
pin_potenciometar = [28]
morse_pins = [14, 27] # jedna ledica za morse kod prikaz i ulaz signala
button_game_pins = [15] # jedno dugme, button zauzima vec ss=16, sck=18, mosi=19!
wire_pins = [17, 20, 21, 22, 26] # sta god ali 5
topics = [b'katane/main_ready',b'katane/game_state',b'katane/game_over']
#___________________________________Pomocne funkcije____________________________________________#
def subscribe(topic, msg):
	global run, main_ready, state, main_timer, spammer
	if topic == b'katane/main_ready' and msg == b'1':
		main_ready = True
		spammer.deinit()
	if topic == b'katane/game_state' and main_ready:
		parsed = ujson.loads(msg)
		print(msg)
		state = int(parsed["state"])
		run = True
		print(run)
	if topic == b'katane/game_over' and msg in (b'Bomba je deaktivirana', b'BOOM'):
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
	print(f'strikes: {strikes} new: {new_strikes}')
	print(f'solved: {solved} new: {len(solved_moduli)}')
	if strikes != new_strikes:
		strikes = new_strikes
		mqtt_conn.publish(b'katane/slave_strike', str(strikes).encode('utf-8'))
	if solved != len(solved_moduli):
		solved = len(solved_moduli)
		mqtt_conn.publish(b'katane/slave_solved', str(solved).encode('utf-8'))

def spam(t):
	mqtt_conn.publish(b'katane/slave_present', b'1')
#___________________________________Spajanje na Wifi____________________________________________#


nic = network.WLAN(network.STA_IF)
nic.active(True)
nic.connect(network_name, network_password)

while not nic.isconnected():
    print('Cekam vezu')
    time.sleep(1)
print("Spojeno")
print(nic.ifconfig())
#___________________________________Game setup____________________________________________#

mqtt_conn = MQTTClient(client_id='Pacacalave', server=SERVER,user='',password='',port=1883)

mqtt_conn.set_callback(subscribe)

mqtt_conn.connect()
for topic in topics:
	mqtt_conn.subscribe(topic,1)

spammer = Timer(period=100, mode=Timer.PERIODIC, callback=spam)

print("SPOJENO NA MQTT")
while not main_ready:
	mqtt_conn.publish(b'katane/slave_present', b'1')
	print('cekam main da se javi da je ziv')
	mqtt_conn.wait_msg()
		

while not run:
	print('cekam informacije o igri...')
	mqtt_conn.wait_msg()
	time.sleep(0.1)


mqtt_conn.publish(b'katane/finalhandshake',b'1')
spammer.deinit()


moduli_pool = [SimonSays(simon_buttons, simon_leds),
				MatricnaGame(state, pins_izlazna, pins_ulazna),
				Button(state, button_game_pins)
                ]

solved_moduli = []	

main_timer = Timer(period=50, mode=Timer.PERIODIC, callback=check)


while run:
	print('game is running...')
	mqtt_conn.check_msg()
	time.sleep(1)

print('Game over!')

for m in moduli_pool:
    m.deinit()
for m in solved_moduli:
    m.deinit()

