from machine import Pin,Timer
import time
import network
from labirint import Labirint
from decoder import Decoder
import random
from umqtt.robust import MQTTClient
import ujson


#___________________________________Glob varijable______________________________________________#
slave_present = False
app_present = False
game_start = False
solved = 0 	
strike = 0
solved_slave = 0
strike_slave = 0
main_timer = Timer(-1)
game_running = False

#___________________________________Pinouts_____________________________________________________#
labirint_pins = [21,22,26,27] # tasteri labirinta lijevo, gore, dole, desno
display_pins = [0, 18,19,16] # labirint display: spi, SCK, MOSI, CSm
encoder_pins = [0,1,2] # jasno clk, dt, sw
segmenti = [4,	5] #
digits = [8,9,10,11,12,13,14] #
rgb = [3,17,28]
#___________________________________Pomocne funkcije____________________________________________#
def subscribe(topic, msg):
	global slave_present, app_present, game_running, game_start, strike_slave, solved_slave
	print(topic.upper())
	if topic == b'katane/slave_present' and msg == b'1':
		slave_present = True
	if topic == b'katane/app_present' and msg == b'1':
		app_present = True
	if topic == b'katane/game_start' and msg == b'1':
		game_running = True
		game_start = True
	if topic == b'katane/slave_solved':
		solved_slave = int(msg)
	if topic == b'katane/slave_strike':
		strike_slave = int(msg)

# postavlja rgb i vraca dozvoljeni broj strikeova i stanje igre
def rgb_randomiser():
	state = random.randint(0, 7) 
	strikes = random.randint(0,3)
	ledice = [Pin(i, Pin.OUT) for i in rgb]
	mask = 1
	for led in ledice:
		led.value(state & mask)
		mask = mask << 1

	return state, strikes

def explode(t):
	global game_running
	mqtt_conn.publish(b'katane/game_over', b'lose')
	main_timer.deinit()
	game_running = False

def check(t):
	global solved, strike, game_running
	solved = 0
	strike = 0
	for m in moduli:
		solved += m.solved
		strike += m.get_strikes()
		print("greske je dao", strike, m)
	if strike + strike_slave > max_strike:
		explode(t)
		print("its  me hi")
	elif solved + solved_slave == 7:
		count_down.deinit()
		mqtt_conn.publish(b'katane/game_over', b'win')
		main_timer.deinit()
		print('ggwp')
		game_running = False

def publish_state(state, max_strike):
	json = '{ "state": ' + str(state) + ',"max_strike": ' + str(max_strike) + ' }'
	mqtt_conn.publish(b'katane/game_state', json.encode('ascii'))

#___________________________________Spajanje na Wifi____________________________________________#

network_name = 'Lab220'
network_password = 'lab220lozinka'

nic = network.WLAN(network.STA_IF)
nic.active(True)
nic.connect(network_name, network_password)

while not nic.isconnected():
    print('Cekam vezu')
    time.sleep(1)
print("spojeno")

print(nic.ifconfig())
#___________________________________Game setup____________________________________________#

mqtt_conn = MQTTClient(client_id='nestonase', server='broker.emqx.io',user='',password='',port=1883)
mqtt_conn.set_callback(subscribe)
mqtt_conn.connect()
mqtt_conn.subscribe(b"katane/#")


while not slave_present:
	print('cekam slave da se javi')
	mqtt_conn.wait_msg()

print("dalje")
while not app_present:
	print('cekam aplikaciju sa telefona da se javi')
	mqtt_conn.wait_msg()

mqtt_conn.publish(b'katane/main_ready', b'1') # javi telefonu da je main spreman da pocne

while not game_start:
	mqtt_conn.wait_msg()
	print('cekam da telefon kaze da igra pocinje')

#____________________________________Game Run_______________________________________#

state, max_strike = rgb_randomiser()

publish_state(state, max_strike) # javi slaveu stanje, a telefonu broj dozvoljenih pokusaja

count_down = Timer(period=3 * 1000 * 60, mode=Timer.ONE_SHOT, callback=explode)

moduli = [Labirint( labirint_pins, display_pins), Decoder(encoder_pins,  digits,segmenti, state)]
main_timer.init(period=100, mode=Timer.PERIODIC, callback=check)


while game_running:
	print('igra u toku...')
	time.sleep(0.5)

