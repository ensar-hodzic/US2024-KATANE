import time
from machine import Pin, Timer

class Decoder:
    brojevi = {
        0: (0, 0, 0, 0, 0, 0, 1),
        1: (1, 0, 0, 1, 1, 1, 1),
        2: (0, 0, 1, 0, 0, 1, 0),
        3: (0, 0, 0, 0, 1, 1, 0),
        4: (1, 0, 0, 1, 1, 0, 0),
        5: (0, 1, 0, 0, 1, 0, 0),
        6: (0, 1, 0, 0, 0, 0, 0),
        7: (0, 0, 0, 1, 1, 1, 1),
        8: (0, 0, 0, 0, 0, 0, 0),
        9: (0, 0, 0, 0, 1, 0, 0)
    }
    rjesenja = [17,73,29,31,7,20,47,97]
    
    
    
    def __init__(self, seed, encoder_pins, segmenti, digits):
        self.clock_wise = Pin(0, Pin.IN)
        self.counter_clock = Pin(1, Pin.IN)
        self.press = Pin(2, Pin.IN) 

        self.brojac = 0
        self.solved = False
        self.strikes = 0

        self.seed = Decoder.rjesenja[seed]

        self.segmenti = [Pin(pin, Pin.OUT) for pin in segmenti]
        self.digits = [Pin(pin, Pin.OUT) for pin in digits]

        self.display = Timer(period=45, mode=Timer.PERIODIC, callback=self.prikaziBroj)

        self.clock_wise.irq(self.handle1, Pin.IRQ_FALLING)
        self.counter_clock.irq(self.handle2, Pin.IRQ_FALLING)
        self.press.irq(self.check, Pin.IRQ_FALLING)
    
    def handle1(self,pin):
        if (self.counter_clock.value() == 1):
            self.brojac += 1

    def handle2(self, pin):
        if (self.clock_wise.value() == 1):
            self.brojac -= 1
    
    def check(self, pin):
        if self.brojac != self.seed:
            self.strikes += 1
        else:
            self.press.irq(None, 0)    
        
        self.brojac = 0

    def prikaziBroj(self, pin):
        cifre = [self.brojac // 10, self.brojac % 10]
        self.digits[0].value(1)
        self.digits[1].value(0)
        t = self.brojevi[cifre[0]]
        for i in range(8):
            self.segmenti[i].value(t[i])
        
        time.sleep(0.02)
        self.digits[0].value(0)
        self.digits[1].value(1)
        t = self.brojevi[cifre[1]]
        for i in range(8):
            self.segmenti[i].value(t[i])
        

    def get_strikes(self):
        return self.strikes
