from machine import Pin,Timer
import time
import network
from umqtt.robust import MQTTClient
import ujson
from labirint import Labirint
from decoder import Decoder
import random
# Raspberry master

# spoji se na internet
import network
import time
from machine import Pin
from umqtt.robust import MQTTClient
import ujson
import gc
gc.enable()

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
spam_slave = Timer(-1)
TIME = 0
MAX_TIME = 180
#___________________________________Pinouts_____________________________________________________#
labirint_pins = [27,26,22,21] # tasteri labirinta lijevo, gore, dole, desno
display_pins = [0, 18,19,16] # labirint display: spi, SCK, MOSI, CSm
encoder_pins = [0,1,2] # jasno clk, dt, sw
segmenti = [4,	5] # odabir cifre
digits = [8,9,10,11,12,13,14] # segmenti na cifri
rgb = [3,17,28]

topics = [b'katane/slave_present' , b'katane/app_present', b'katane/game_start',b'katane/slave_solved', b'katane/finalhandshake',b'katane/slave_strike']
#___________________________________Pomocne funkcije____________________________________________#
def subscribe(topic, msg):
	global slave_present, app_present, game_running, game_start, strike_slave, solved_slave, spam_slave
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
		print("slave strike ", strike_slave)
	if topic == b'katane/finalhandshake':
		spam_slave.deinit()

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
	global game_running, mqtt_conn, main_timer
	print('usao')
	mqtt_conn.publish(b'katane/game_over', b'BOOM')
	print('izasao')
	main_timer.deinit()
	game_running = False

def check(t):
	global solved, strike, game_running
	mqtt_conn.check_msg()
	new_solved = solved_slave
	new_strike = strike_slave
	print('provjera')
	for m in moduli:
		new_solved += int(m.solved)
		new_strike += m.get_strikes()
		print("greske je dao", strike, m)
	if new_strike > max_strike:
		explode(t)
		print("its  me hi")
	elif new_solved  >= 5:
		count_down.deinit()
		print('pobjeda')
		mqtt_conn.publish(b'katane/game_over', b'Bomba je deaktivirana')
		main_timer.deinit()
		print('ggwp')
		game_running = False
	if new_strike != strike:
		strike = new_strike
		mqtt_conn.publish(b'katane/strikes', str(strike).encode('ascii'))
	if new_solved != solved:
		solved = new_solved
		mqtt_conn.publish(b'katane/solved', str(solved).encode('ascii'))

def publish_state(state, max_strike):
	json = '{ "state": ' + str(state) + ',"max_strike": ' + str(max_strike) + ' }'
	mqtt_conn.publish(b'katane/game_state', json.encode('ascii'),1)
	mqtt_conn.publish(b'katane/solved', b'0')
	mqtt_conn.publish(b'katane/strikes', b'0')
	mqtt_conn.publish(b'katane/game_over', b'Igra u toku')

def post_time(t):
	global TIME
	mqtt_conn.publish(b'katane/time', str(TIME).encode('ascii'))
	TIME += 1

#___________________________________Spajanje na Wifi____________________________________________#

network_name = "LabUSProjekat"
network_password = 'hastafor77'

nic = network.WLAN(network.STA_IF)
nic.active(True)
nic.connect(network_name, network_password)




while not nic.isconnected():
    print('Cekam vezu')
    time.sleep(1)
print("spojeno")

print(nic.ifconfig())
#___________________________________Game setup____________________________________________#
SERVER = '192.168.43.69'

mqtt_conn = MQTTClient(client_id='2', server=SERVER,user='',password='',port=1883)

#mqtt_conn.set_last_will(b'katane/game_over', b'aaaaa', retain=True)

mqtt_conn.set_callback(subscribe)

mqtt_conn.connect()
print('jajajjaja')


for topic in topics:
    mqtt_conn.subscribe(topic,1)


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


#spam_slave = Timer(period=1000, mode=Timer.PERIODIC, callback=lambda t: publish_state(state, max_strike))

count_down = Timer(period= MAX_TIME * 1000 , mode=Timer.ONE_SHOT, callback=explode)

moduli = [Labirint( labirint_pins, display_pins,state),
          Decoder(encoder_pins,  segmenti,digits, state)]
main_timer.init(period=500, mode=Timer.PERIODIC, callback=check)
cdtimer = Timer(period=1000, mode = Timer.PERIODIC, callback=post_time)
while game_running:
	print('igra u toku...')
	time.sleep(0.5)
	
	
print('opa')
explode(1)

for m in moduli:
    m.deinit()
    
cdtimer.deinit() 
#machine.reset()

