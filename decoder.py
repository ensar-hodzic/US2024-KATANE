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


    def __init__(self, seed, encoder_pins, segmenti, digits):
        self.clock_wise = Pin(encoder_pins[0], Pin.IN)
        self.counter_clock = Pin(encoder_pins[1], Pin.IN)
        self.press = Pin(encoder_pins[2], Pin.IN) 

        self.brojac = 0
        self.solved = False
        self.strikes = 0

        self.seed = Decoder.rjesenja[seed]

        self.segmenti = [Pin(pin, Pin.OUT) for pin in segmenti]
        self.digits = [Pin(pin, Pin.OUT) for pin in digits]

        self.display_timer = Timer(period=45, mode=Timer.PERIODIC, callback=self.display)

        self.clock_wise.irq(self.handle_clockwise, Pin.IRQ_FALLING)
        self.counter_clock.irq(self.handle_counterclock, Pin.IRQ_FALLING)
        self.press.irq(self.check, Pin.IRQ_FALLING)
    
    def handle_clockwise(self,pin):
        if (self.counter_clock.value() == 1):
            self.brojac += 1

    def handle_counterclock(self, pin):
        if (self.clock_wise.value() == 1):
            self.brojac -= 1
    
    def check(self, pin):
        if self.brojac != self.seed:
            self.strikes += 1
        else:
            self.press.irq(None, 0)  
            self.solved = True
            self.display_timer.deinit()  
        
        self.brojac = 0

    def display_digit(self, n):
        l = self.arrSeg[n]
        for i in range(8):
            self.segments[i].value(l[i])

    def reset_digits(self):
        for i in range(4):
            self.digits[i].value(False)

    def display(self, t):
        d, j = self.brojac // 10, self.brojac % 10

        self.reset_digits()
        self.digits[0].value(True)
        self.display_digit(d)
        
        time.sleep(0.020)

        self.digits[0].value(True)
        self.digits[1].value(False)
        self.display_digit(j)

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
        self.display_timer.deinit()
