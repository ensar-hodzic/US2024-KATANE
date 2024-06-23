from machine import Pin, Timer

class Decoder:
    rjesenja = [17,73,29,31,7,20,47,97]
    clk_okinut = dt_okinut = smjer = greska = solved = False
    brojac = 0
    greske = 0

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

    """
    pins prima 3 elementa [clk,dt,sw]
    segmenti prima 7 elemenata 
    digits 2 
    seed 0-7
    """
    def __init__(self, pins: list, segmenti:list, digits:list, seed):
        self.clk = Pin(pins[0], Pin.IN)
        self.dt = Pin(pins[1], Pin.IN)
        self.sw = Pin(pins[2], Pin.IN)
        self.rjesenje = self.rjesenja[seed]
        self.segmenti = [Pin(pin, Pin.OUT) for pin in segmenti]
        self.digits = [Pin(pin, Pin.OUT) for pin in digits]

        self.prikazujBrojeve = Timer(period=20, mode=Timer.PERIODIC, callback=self.prikaziBroj)
        
        self.clk.irq(trigger=Pin.IRQ_FALLING, handler=self.okinutCLK)
        self.dt.irq(trigger=Pin.IRQ_FALLING, handler=self.okinutDT)
        self.sw.irq(trigger=Pin.IRQ_FALLING, handler=self.potvrdi)

    def okinutCLK(self, pin):
        if not self.greska and not self.solved:        
            self.clk_okinut = True
            if self.dt_okinut:
                if self.brojac > 0:
                    self.brojac -= 1
                self.clk_okinut = self.dt_okinut = False
    
    def okinutDT(self, pin):
        if not self.greska and not self.solved:        
            self.dt_okinut = True
            if self.clk_okinut:
                if self.brojac < 99:
                    self.brojac += 1
                self.clk_okinut = self.dt_okinut = False
    
    def potvrdi(self, pin):
        if not self.greska and not self.solved:        
            if self.brojac == self.rjesenje:
                self.solved = True
                prikazujUspjeh=Timer(period=500,mode=Timer.PERIODIC, callback=self.prikaziUspjeh)
            else:
                self.greska=True
                self.greske += 1
                vratiNaNulu=Timer(period=100,mode=Timer.PERIODIC, callback=self.prikaziGresku)
    
    prikaziCifru = 0
    def prikaziBroj(self, pin):
        cifre = [self.brojac // 10, self.brojac % 10]
        if self.prikaziCifru == 0:
            self.digits[1].off()
            for segment, state in zip(self.segmenti, self.brojevi[cifre[0]]):
                segment.value(state)
            self.digits[0].on()
        else:
            self.digits[0].off()
            for segment, state in zip(self.segmenti, self.brojevi[cifre[1]]):
                segment.value(state)
            self.digits[1].on()
        self.prikaziCifru = (self.prikaziCifru + 1) % 2


    def prikaziGresku(self,pin):
        if(self.brojac>0):
            self.brojac-=1
        else:
            self.greska=False
            pin.deinit()

    i=0
    def prikaziUspjeh(self,pin):
        if self.i == 0 :
            self.prikazujBrojeve.deinit()
            for segment in self.segmenti:
                segment.value(1)
        else:
            self.prikazujBrojeve.init(period=20, mode=Timer.PERIODIC, callback=self.prikaziBroj)
        self.i = (self.i + 1) % 2
    

