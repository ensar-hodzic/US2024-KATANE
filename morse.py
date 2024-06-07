from machine import ADC, Pin, Timer


class Morse:
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
	def __init__(self, word:str, pins: list, frequency:float, duty:float = 0.5):
		self.solved = False
		self.led = Pin(pins[0], Pin.OUT)
		self.analog = ADC(Pin(pins[1], Pin.IN))
		self.signal = signal
		self.led_array = _convert(upper(word))
		self.curr = 0		
		self.timer = Timer(period=T, mode=Timer.PERIODIC, callback=self._morse)
		self.target = target(duty)
		# uzorkuj signal na frequency*10 kad je dobar modul je rijesen
		rate = int(1 / (10 * frequency) * 1000)
		self.buffer = [0] * 10
		self.sampler = Timer(period=rate, mode=Timer.PERIODIC, callback=self._sample)
		self.comparator = Timer(period=rate*10, mode=Timer.PERIODIC, callback=self._check)

	def target(duty):
		arr = [0.0] * 10
		for i in range(int(duty * 10)):
			arr[i] = 1.0
		return arr

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

	def _morse(self):
		led.value(self.led_array[self.curr])
		self.curr += 1
		self.curr %= len(self.led_array)
	
	def _sample(self):
		val = u16tofloat(self.analog.read_u16())
		self.buffer[-1] = val
		self.buffer = shift(self.buffer)


	def u16tofloat(val: int) -> float:
		if val > 0.8 * 65535:
			return 1.0 
		elif val < 0.2 * 65535:
			return 0.0
		else:
			return 0.5

	def _check(self):
		good = False
		eps = 1e-5
		for i in range(len(self.buffer)):
			good &= abs(self.buffer[i] - self.target[i]) < eps
		if good: # MODUL RIJESEN PRESTANI MJERITI I PRIKAZIVATI
			self.sampler.deinit()
			self.timer.deinit()
			self.comparator.deinit()
			self.solved = True

	def solved(): # OVO KORISTITE DA VIDITE DA LI JE MODUL RIJESEN
		return self.solved











