from machine import ADC, Pin, Timer


class Morse:
	code_book = [('TVRD', 1500, 0.5), ('2024', 2500, 0.5), ('US24', 1000, 0.5),
			('BOMB', 1500, 0.6), ('BOOM', 2500, 0.6), ('KAFA', 1000, 0.6),
			('SOS', 1500, 0.4), ('ZELJO', 2500, 0.4)]
	morse = {
	    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
	    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
	    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
	    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
	    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
	    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
	    'Y': '-.--',  'Z': '--..',
	    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
	    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
	    '8': '---..', '9': '----.',
	    '.': '.-.-.-', ',': '--..--', '?': '..--..', '=': '-...-'
	}
	T = 500 # dot - jedan T, dash - tri T, space - jedan T
	# word je rijec koja se prikazuje na ledicu u morsovom kodu
	# pins su liste brojeva pinova oblika [LED_PIN_NUM,AD_IN]
	# frequency je frekvencija trazenog kvadratnog talasa
	# duty je duty cycle trazenog signala [0.0, 1.0]
	def __init__(self, state, pins: list):
		word, frequency, duty = code_book[state]

		self.solved = False
		self.led = Pin(pins[0], Pin.OUT)
		self.analog = ADC(Pin(pins[1], Pin.IN))

		self.led_array = self._convert(word.upper())
		self.curr = 0		

		self.target = self.target(duty) * 3
		# uzorkuj signal na frequency*10 kad je dobar modul je rijesen
		rate = int(1 / (10 * frequency) * 1000)
		self.buffer = [0] * 30
		
		self.timer = Timer(-1)
		self.sampler = Timer(-1)
		self.comparator = Timer(-1)
		
		self.timer.init(period=self.T, mode=Timer.PERIODIC, callback=self._morse)
		self.sampler.init(period=rate, mode=Timer.PERIODIC, callback=self._sample)
		self.comparator.init(period=rate*10, mode=Timer.PERIODIC, callback=self._check)
    
	@staticmethod
	def target(duty):
		arr = [0.0] * 10
		for i in range(int(duty * 10)):
			arr[i] = 1.0
		return arr

	@staticmethod
	def _convert(word):
		arr = []
		for c in word:
			arr.append(0)
			if c == '/':
				arr.append(0)
			elif c == '.':
				arr.append(1)
			elif c == '-':
				arr += [1, 1, 1]
			arr.append(0)
		return arr

	def _morse(self, t):
		self.led.value(self.led_array[self.curr])
		self.curr += 1
		self.curr %= len(self.led_array)
	
	def _sample(self, t):
		val = self.u16tofloat(self.analog.read_u16())
		self.shift()
		self.buffer[-1] = val

	def shift(self):
		self.buffer = self.buffer[1:]
		self.buffer.append(0)


	@staticmethod
	def u16tofloat(val: int) -> float:
		if val > 0.8 * 65535:
			return 1.0 
		elif val < 0.2 * 65535:
			return 0.0
		else:
			return 0.5

	def _check(self, t):
		good = True
		eps = 1e-5
		for i in range(len(self.buffer)):
			good &= abs(self.buffer[i] - self.target[i]) < eps
		if good: # MODUL RIJESEN PRESTANI MJERITI I PRIKAZIVATI
			self.sampler.deinit()
			self.timer.deinit()
			self.comparator.deinit()
			self.solved = True

	def solved(self): # OVO KORISTITE DA VIDITE DA LI JE MODUL RIJESEN
		return self.solved