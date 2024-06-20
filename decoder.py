from machine import Pin, Timer

class Decoder:
    clk_okinut = dt_okinut = smjer = False
    brojac=0
    greske=0
    prikaziCifru=0
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

    # pins: clk, dt, sw
    def __init__(self, pins:list, segmenti, digits, rjesenje)
        self.solved=False
        self.clk = Pin(pins[0], Pin.IN) # 
        self.dt = Pin(pins[1], Pin.IN) # decoder dijelovi
        self.sw = Pin(pins[2], Pin.IN) # 
        self.rjesenje=10 * rjesenje + 10
        self.segmenti=[Pin(pin,Pin.OUT) for pin in segmenti]
        self.digits = [Pin(pin,Pin.OUT) for pin in digits]
        
        self.prikazujBrojeve=Timer(-1)
        self.prikazujBroj.init(period=20,mode=Timer.PERIODIC,callback=self.prikaziBroj)
        
        self.clk.irq(trigger=Pin.IRQ_FALLING, handler=self.okinutCLK)
        self.dt.irq(trigger=Pin.IRQ_FALLING, handler=self.okinutDT)
        self.sw.irq(trigger=Pin.IRQ_FALLING, handler=self.potvrdi)

    def okinutCLK(self,pin):
        self.clk_okinut = True
        if (self.dt_okinut):
            if self.brojac != 99:
                self.brojac=self.brojac+1
            self.clk_okinut = self.dt_okinut = False
    
    def okinutDT(self,pin):
        self.dt_okinut = True
        if (self.clk_okinut):
            if self.brojac != 0:
                self.brojac=self.brojac-1
            self.clk_okinut = self.dt_okinut = False
    
    def potvrdi(self,pin):
        if self.brojac == self.rjesenje:
            self.solved=True
            print("svaka cast")
        else: 
            self.greske = self.greske+1

#moguci problemi
#dodaj prikaz kad potrefis
    def prikaziBroj(self,pin):
        cifre = [brojac%10,brojac/10]
        if self.prikaziCifru == 0:
            self.digits[1].off()
            for segment, state in zip(self.segmenti, self.brojevi[cifre[0]]):
                segment.value(state)
            self.digits[0].on()
        else:
            self.digits[0].off
            for segment, state in zip(self.segmenti, self.brojevi[cifre[1]]):
                segment.value(state)
            self.digits[1].on()
        self.prikaziCifru=(self.prikaziCifru+1)%2
