# Raspberry master

# spoji se na internet
import network
import time
from machine import Pin
from umqtt.robust import MQTTClient
import ujson


network_name = 'Wifi'
network_password = 'password'

nic = network.WLAN(network.STA_IF)
nic.activate(True)
nic.connect(network_name, network_password)

while not nic.isconnected():
    print('Cekam vezu')
    time.sleep(1)



# okini RGB randomiser

state = rgb_randomiser()


mqtt_conn = MQTTClient(clientid='master', server='broker.hivemq.com', user='', password='', port=1883)
mqtt_conn.set_callback(subscription)
mqtt_conn.connect()


moduli=[b"katane/morse", b"katane/simon_says", b"katane/button_press", b"katane/wires", b"katane/password"]# lista modula na slaveu
mqtt_conn.subscribe(moduli)
# daj konfiguraciju slaveu



# pokreni igru

