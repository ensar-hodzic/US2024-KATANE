import random
import time
from machine import Pin, Timer

class Labirint:
    cifra = [
          [ 1, 2, 3, 'A' ],
          [ 4, 5, 6, 'B' ],
          [ 7, 8, 9, 'C' ],
          [ '*', 0, '#', 'D' ]
        ]
    T = 50
    def __init__(self, pins_izlazna, pins_ulazna):
        self.izlazMatricna = [ Pin(k ,Pin.OUT) for k in pins_izlazna] 
        self.ulazMatricna = [ Pin(i, Pin.IN, Pin.PULL_DOWN) for i in pins_ulazna]
        self.debounce = 0
        self.labirintPut = [0,0,0,0,0,0,0,0]
        self.brojacLabirint=0
        self.br_gresaka = 0
        self.solved = False

        self.generisiPut()

        self.timerMat=Timer(mode=Timer.PERIODIC, period=self.T, callback=self.Labirint) ##Igrati se sa period
    

    def Labirint(self, tim):
        if time.ticks_ms()-self.debounce<400:
            return
        for i in range(4):
            self.izlazMatricna[i].value(1)
            for j in range(4):
                if self.ulazMatricna[j].value() == 1:
                    self.izlazMatricna[i].value(0)
                    if self.cifra[i][j]==self.labirintPut[self.brojacLabirint]:
                        self.brojacLabirint+=1
                        print("Bravo nastavi još samo "+str(8-self.brojacLabirint)+" koraka")
                    else:
                        print("POGREŠAN PUT")
                        self.br_gresaka += 1
                    if self.brojacLabirint==8:
                        print("Izašao si iz lavirinta i bomba no kaput")
                        self.brojacLabirint=0
                        self.solved = True
                        self.timerMat.deinit()
                        self.debounce=0
                        gameStart=False
                    self.debounce=time.ticks_ms()
            self.izlazMatricna[i].value(0)

    def generisiPut(self):
        for i in range(8):
            self.labirintPut[i]=random.choice([2,4,6,8])

    def get_path(self):
        return self.labirintPut