class MainKatane:
	def __init__(self, state, mqtt_conn):
		self.mqtt = mqtt_conn
		self.strikes = state % 4 # dozvoljene greske

		self.solved_vector = self.