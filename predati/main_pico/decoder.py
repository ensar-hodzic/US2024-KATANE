import time
from machine import Pin, Timer

class Decoder:
    rjesenja = [17,73,29,31,7,20,47,97]
    
    num2seg = {0: [0,1,2,3,4,5], 
            1: [1,2],
            2: [0,1,3,4,6],
            3: [0,1,2,3,6],
            4: [1,2,5,6],
            5: [0,2,3,5,6],
            6: [0,2,3,4,5,6],
            7: [0,1,2],
            8: [0,1,2,3,4,5,6],
            9: [0,1,2,3,5,6]}
    arrSeg = [[1,1,1,1,1,1,0],
            [0,1,1,0,0,0,0],
            [1,1,0,1,1,0,1],
            [1,1,1,1,0,0,1],
            [0,1,1,0,0,1,1],
            [1,0,1,1,0,1,1],
            [1,0,1,1,1,1,1],
            [1,1,1,0,0,0,0],
            [1,1,1,1,1,1,1],
            [1,1,1,1,0,1,1]]


    def __init__(self, encoder_pins, segmenti, digits,seed):
        self.clock_wise = Pin(encoder_pins[0], Pin.IN, Pin.PULL_UP)
        self.counter_clock = Pin(encoder_pins[1], Pin.IN, Pin.PULL_UP)
        self.press = Pin(encoder_pins[2], Pin.IN) 

        self.brojac = 0
        self.solved = False
        self.strikes = 0

        self.seed = Decoder.rjesenja[seed]

        self.segmenti = [Pin(pin, Pin.OUT) for pin in segmenti]
        self.digits = [Pin(pin, Pin.OUT) for pin in digits]

        self.display_timer = Timer(period=45, mode=Timer.PERIODIC, callback=self.display)

        self.clkdb = time.ticks_ms()
        self.swdb = time.ticks_ms()
        self.btn = time.ticks_ms()

        self.clock_wise.irq(self.handle1, Pin.IRQ_RISING)
        self.counter_clock.irq(self.handle2, Pin.IRQ_RISING)
        self.press.irq(self.check, Pin.IRQ_RISING)
    
    def handle1(self,pin):
        #if  time.ticks_ms() - self.clkdb < 100:
         #   return
        print('h1')
        if (self.counter_clock.value() == 1):
            self.brojac += 1
        self.clkdb = time.ticks_ms()

    def handle2(self, pin):
        #if  time.ticks_ms() - self.swdb < 100:
         #   return    
        
        print('h2')
        if (self.clock_wise.value() == 1):
            self.brojac -= 1
        self.swdb = time.ticks_ms()
    
    def check(self, pin):
        print('h3')
        #if  time.ticks_ms() - self.btn < 100:
            #return
        if self.brojac != self.seed:
            self.strikes += 1
        else:
            self.press.irq(None, 0)  
            self.solved = True
            self.display_timer.deinit()  
        self.btn = time.ticks_ms()
        self.brojac = 0

    def display_digit(self, n):
        l = self.arrSeg[n]
        for i in range(7):
            self.digits[i].value(1 - l[i])

    def reset_digits(self):
        for i in range(2):
            self.segmenti[i].value(True)

    def display(self, t):
        d, j = self.brojac // 10, self.brojac % 10
        self.reset_digits()
        self.zero()
        self.segmenti[0].value(False)
        self.display_digit(d)
        
        time.sleep(0.020)

        self.segmenti[0].value(True)
        self.segmenti[1].value(False)
        self.zero()
        self.display_digit(j)
        
    def zero(self):
        for i in range(7):
            self.digits[i].value(1)
        
    def test_display(self):
        self.reset_digits()
        for s in self.segmenti:
            self.reset_digits()
            s.value(False)
            for i in range(10): 
                self.display_digit(i)
                time.sleep(1)

    def get_strikes(self):
        return self.strikes
    def deinit(self):
        self.clock_wise.irq(None,0)
        self.counter_clock.irq(None,0)
        self.press.irq(None,0)
        self.display_timer.deinit()
    

