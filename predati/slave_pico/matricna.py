from machine import Timer, Pin
import time
class MatricnaGame:
    password_list = [
        [0,0,0,0], [1,2,3,4], [1,9,8,7], [5,3,9,7],
        [3,9,7,3], [8,8,9,2], [4,9,1,1], [8,6,0,3]
    ]
    cifra = [
          [ 1, 2, 3, 'A' ],
          [ 4, 5, 6, 'B' ],
          [ 7, 8, 9, 'C' ],
          [ '*', 0, '#', 'D' ]
        ]
    T = 50
    def generisiSifruMatricna(self, state):
        self.sifraMatricna=self.password_list[state]

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
        print(self.sifraMatricna)
        if self.sifraMatricna==self.korisnikSifra and self.brojacMatricna==4:
            self.timerMat.deinit()
            self.korisnikSifra=[0,0,0,0]
            self.brojacMatricna=0
            self.debounce=0
            self.solved = True
            return
        if self.brojacMatricna==4:
            self.brojacMatricna=0
            self.korisnikSifra=[0,0,0,0]
            self.br_gresaka += 1

    # pins_izlazna - brojevi pinova za izlazMatrica
    # pins_ulazna - brojevi pinova za ulazMatrica
    def __init__(self, state, pins_izlazna, pins_ulazna):
        self.sifraMatricna=[0,0,0,0]
        self.brojacMatricna=0
        self.solved = False
        
        self.korisnikSifra=[0,0,0,0]
        self.brojevi=[0,0,2,0] #Koliko vremena im daješ
        self.debounce=0
        self.izlazMatricna = [ Pin(k ,Pin.OUT) for k in pins_izlazna] 
        self.ulazMatricna = [ Pin(i, Pin.IN, Pin.PULL_DOWN) for i in pins_ulazna]

        self.br_gresaka = 0

        self.generisiSifruMatricna(state)

        self.timerMat=Timer(-1)  #TIMER
        self.timerMat.init(mode=Timer.PERIODIC, period=self.T, callback=self.postaviSifru) ##Igrati se sa period

    def solved(self):
        return self.solved

    def get_sifra(self):
        return self.sifraMatricna

    def get_strikes(self):
        return self.br_gresaka
    def deinit(self):
        self.timerMat.deinit()

