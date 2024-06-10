from machine import Pin, ADC, Timer

class Potenciometar:
    T = 100
    eps = 5 # tolerancija 
    # pins - broj pina za potenciometar
    def __init__(self, pins):
        self.solved = False
        self.potenciometar = ADC(pins[0])
        self.sifra = random.randrange(0,100)
        self.timerPot = Timer(mode=Timer.PERIODIC, period=self.T, callback=self.PotenciometarGame)


    def PotenciometarGame(self, t):
        print(int(self.potenciometar.read_u16()/65535*100))
        if abs(int(self.potenciometar.read_u16()/65535*100) - self.sifra) < self.eps:
            print("BRAVO NO BOMBA KAPUT ON POTENCIOMETAR GAME")
            self.timerPot.deinit()
            self.solved = True

    def solved(self):
        return self.solved

    def get_sifra(self): #TODO: u main poslati app koja je sifra
        return self.sifra
            