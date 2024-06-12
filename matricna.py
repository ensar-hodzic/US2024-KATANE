from machine import Timer, Pin

class MatricnaGame:
    cifra = [
          [ 1, 2, 3, 'A' ],
          [ 4, 5, 6, 'B' ],
          [ 7, 8, 9, 'C' ],
          [ '*', 0, '#', 'D' ]
        ]
    T = 50
    def generisiSifruMatricna(self):
        for i in range(3):
            self.sifraMatricna[i]=random.randrange(0,9)

    def postaviSifru(self, irq):
        if time.ticks_ms()-self.debounce<400:
            return
        for i in range(4):
            self.izlazMatricna[i].value(1)
            for j in range(4):
                if self.ulazMatricna[j].value() == 1:
                    self.izlazMatricna[i].value(0)
                    self.korisnikSifra[self.brojacMatricna] = self.cifra[i][j] 
                    self.brojacMatricna+=1
                    self.debounce=time.ticks_ms()
                    print(self.cifra[i][j])         
            self.izlazMatricna[i].value(0)
        if self.sifraMatricna==self.korisnikSifra and self.brojacMatricna==4:
            print("BRAVO NO BOMBA KAPUT ON MATRCINA TASTATURA GAME")
            self.timerMat.deinit()
            self.korisnikSifra=[0,0,0,0]
            self.brojacMatricna=0
            self.debounce=0
            #gameStart=False
            self.solved = True
            return
        if self.brojacMatricna==4:
            print("POGRESNA SIFRA")
            self.brojacMatricna=0
            self.korisnikSifra=[0,0,0,0]
            self.br_gresaka += 1

    # pins_izlazna - brojevi pinova za izlazMatrica
    # pins_ulazna - brojevi pinova za ulazMatrica
    def __init__(self, pins_izlazna, pins_ulazna):
        self.sifraMatricna=[0,0,0,0]
        self.brojacMatricna=0
        self.solved = False
        
        self.korisnikSifra=[0,0,0,0]
        self.brojevi=[0,0,2,0] #Koliko vremena im daješ
        self.debounce=0
        self.izlazMatricna = [ Pin(k ,Pin.OUT) for k in pins_izlazna] 
        self.ulazMatricna = [ Pin(i, Pin.IN, Pin.PULL_DOWN) for i in pins_ulazna]

        self.br_gresaka = 0

        self.generisiSifruMatricna()

        self.timerMat=Timer(-1)  #TIMER ZA POTENCIOMETAR GAME
        self.timerMat.init(mode=Timer.PERIODIC, period=self.T, callback=self.postaviSifru) ##Igrati se sa period

    def solved(self):
        return self.solved

    def get_sifra(self):
        return self.sifraMatricna

    def get_strikes(self):
        return self.br_gresaka