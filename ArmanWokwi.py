from machine import ADC,Pin,Timer 
from utime import sleep
import random

buttons =[Pin(0, Pin.IN),Pin(1, Pin.IN),Pin(2, Pin.IN),Pin(3, Pin.IN)]

gameStart=False ##SLUZI KO DEBOUNCER I ZNAMO KAD JE UPALJENA NEKA IGRA

##TIMER
##########################################################################################
pozicije=[Pin(4,Pin.OUT),Pin(5,Pin.OUT),Pin(6,Pin.OUT),Pin(7,Pin.OUT)]

pins = [
    Pin(8, Pin.OUT),  # A
    Pin(9, Pin.OUT),  # B
    Pin(10, Pin.OUT),  # C
    Pin(11, Pin.OUT),  # D
    Pin(12, Pin.OUT),  # E
    Pin(13, Pin.OUT),  # F
    Pin(14, Pin.OUT),  # G
    Pin(15,Pin.OUT)
]


digits = [
    [0, 0, 0, 0, 0, 0, 1,1], # 0
    [1, 0, 0, 1, 1, 1, 1,1], # 1
    [0, 0, 1, 0, 0, 1, 0,1], # 2 
    [0, 0, 0, 0, 1, 1, 0,1], # 3
    [1, 0, 0, 1, 1, 0, 0,1], # 4
    [0, 1, 0, 0, 1, 0, 0,1], # 5
    [0, 1, 0, 0, 0, 0, 0,1], # 6
    [0, 0, 0, 1, 1, 1, 1,1], # 7
    [0, 0, 0, 0, 0, 0, 0,1], # 8
    [0, 0, 0, 0, 1, 0, 0,1]  # 9
]
def postavi1(trenutni): # PALI A B C D E F G
    for j in range(len(pins)):
        pins[j].value(digits[trenutni][j])

def postavi(brojevi): # UGASI SVE PA POSTAVI SVAKI BROJ POJEDINACNO I UGASI
    for i in range(4):
        pozicije[i].on()
    for i in range(4):
        pozicije[i].off()
        postavi1(brojevi[i])
        sleep(0.02)
        pozicije[i].on()


def popravi(brojevi): # POPRAVLJA KAD SE SMANJUJE I POVECAVA BROJ
    for i in range(3,0,-1):
        if brojevi[i]>9:
            brojevi[i]=0
            brojevi[i-1]+=1
        else:
             break
    for i in range(3,0,-1):
        if brojevi[i]<0:
            brojevi[i]=9
            brojevi[i-1]-=1
        else:
            break
    if brojevi[0]<0:
        for i in range(4):
            brojevi[i]=9
    if brojevi[0]>9:
        for i in range(4):
            brojevi[i]=0
    return brojevi

brojevi=[0,0,0,0]
timer=Timer(-1) #TIMER ZA SAT
timer.deinit()
timerPrikazivanje=Timer(-1)
timerPrikazivanje.deinit()


def TimerOn():
    global timer,timerPrikazivanje
    timer.init(mode=Timer.PERIODIC, period=1000, callback=Odbrojavanje)
    timerPrikazivanje.init(mode=Timer.PERIODIC, period=500, callback=Prikaz) 
    ##NAMEJSTITI PERIOD DA LJEPSE ISPISUJE NA LED INDIKATORU ILI DODAVANJE SLEEP U POSTAVI

def TimerOff():
    global timer
    timer.deinit()
    timerPrikazivanje.deinit()
    postavi([0,0,0,0])

def Prikaz(tim):    ##PRIKAZUJE NA LED INDIKATORU
    global brojevi,timerPrikazivanje
    postavi(brojevi)

def Odbrojavanje(timer):    ##ODBROJAVA SEKUNDI PO SEKUND I UPDATE BROJEVI
    global brojevi,gameStart
    brojevi[3]-=1
    popravi(brojevi)
    if brojevi[0]==9:   ##KAD OD [0,0,0,0] ODUZMEMO 1 POPRAVI CE STAVITI [9,9,9,9]
        brojevi=[0,0,0,0]
        print("BOMBAAA")
        timer.deinit()
        timerPot.deinit()   #Gasi potenciometar games
        timerMat.deinit()   #Gasi matricna games
        gameStart=False

##PotenciometarGame
##########################################################################################
potenciometar=ADC(28)
sifra=0
timerPot=Timer(-1)  #TIMER ZA POTENCIOMETAR GAME
timerPot.deinit()

def PotenciometarGame(tim):
    global timer,sifra,gameStart,timerPot
    print(int(potenciometar.read_u16()/65535*100))
    if int(potenciometar.read_u16()/65535*100)==sifra:
        TimerOff()
        print("BRAVO NO BOMBA KAPUT ON POTENCIOMETAR GAME")
        timerPot.deinit()
        gameStart=False

def StartPotenciometarGame(irq):
    global timerPot,brojevi,sifra,gameStart
    if gameStart:
        return
    gameStart=True
    brojevi=[0,0,2,0] #Koliko vremena im daješ
    sifra=random.randrange(0,100)
    print("PODESI VRIJEDNOST POTENCIOMETRA NA TRAŽENU")
    print("Šifra je "+str(sifra)) ##KASNIJE POSLATI  DRUGOM IGRAČU
    TimerOn()
    timerPot.init(mode=Timer.PERIODIC, period=1000, callback=PotenciometarGame)

##MATRICNII
##########################################################################################
izlazMatricna = [ Pin(26 ,Pin.OUT),Pin(22 ,Pin.OUT),Pin(21 ,Pin.OUT),Pin(20 ,Pin.OUT) ] 
ulazMatricna = [ Pin(i, Pin.IN, Pin.PULL_DOWN) for i in range(19, 15,-1)]

cifra = [
  [ 1, 2, 3, 'A' ],
  [ 4, 5, 6, 'B' ],
  [ 7, 8, 9, 'C' ],
  [ '*', 0, '#', 'D' ]
]

sifraMatricna=[0,0,0,0]
brojacMatricna=0
timerMat=Timer(-1)  #TIMER ZA POTENCIOMETAR GAME
timerMat.deinit()
korisnikSifra=[0,0,0,0]
brojevi=[0,0,2,0] #Koliko vremena im daješ


def generisiSifruMatricna():
    global sifraMatricna
    for i in range(3):
        sifraMatricna[i]=random.randrange(0,9)

def postaviSifru(irq):
    global sifraMatricna,izlazMatricna,ulazMatricna,korisnikSifra,brojacMatricna,gameStart
    for i in range(4):
        izlazMatricna[i].value(1)
        for j in range(4):
            if ulazMatricna[j].value() == 1:
                izlazMatricna[i].value(0)
                korisnikSifra[brojacMatricna] = cifra[i][j] 
                brojacMatricna+=1
                print(cifra[i][j])
                sleep(0.2)          ##Sleep da ima mala pauza izmedju unosa da ne mozemo drzati na matricnoj
        izlazMatricna[i].value(0)
    if sifraMatricna==korisnikSifra and brojacMatricna==4:
        TimerOff()
        print("BRAVO NO BOMBA KAPUT ON MATRCINA TASTATURA GAME")
        timerMat.deinit()
        korisnikSifra=[0,0,0,0]
        brojacMatricna=0
        gameStart=False
        return
    if brojacMatricna==4:
        print("POGRESNA SIFRA")
        brojacMatricna=0
        korisnikSifra=[0,0,0,0]
    
def StartMatricnaGame(irq):
    global brojevi,timerMat,gameStart
    if gameStart:
        return
    gameStart=True
    generisiSifruMatricna()
    print("UKUCAJ ŠIFRU NA MATIČNOJ TASTATURI")
    print(sifraMatricna) ##KASNIJE POSLATI DRUGOM KORISNIKU SIFRU
    brojevi=[0,0,2,0] #Koliko vremena im daješ
    TimerOn()
    timerMat.init(mode=Timer.PERIODIC, period=50, callback=postaviSifru) ##Igrati se sa period

##LABIRINT (KORISTIMO DEKLARACIJE IZ PRETHODNE IGRICE)
##########################################################################################

labirintPut=[0,0,0,0,0,0,0,0] ##POGODITI 8 smjerova
brojacLabirint=0

def generisiPut():
    global labirintPut
    for i in range(8):
        labirintPut[i]=random.choice([2,4,6,8])

def Labirint(tim):
    global labirintPut,brojacLabirint,gameStart
    for i in range(4):
        izlazMatricna[i].value(1)
        for j in range(4):
            if ulazMatricna[j].value() == 1:
                izlazMatricna[i].value(0)
                if cifra[i][j]==labirintPut[brojacLabirint]:
                    brojacLabirint+=1
                    print("Bravo nastavi još samo "+str(8-brojacLabirint)+" koraka")
                else:
                    print("POGREŠAN PUT")
                if brojacLabirint==8:
                    print("Izašao si iz lavirinta i bomba no kaput")
                    brojacLabirint=0
                    TimerOff()
                    timerMat.deinit()
                    gameStart=False
                sleep(0.2)       ##Sleep da ima mala pauza izmedju unosa da ne mozemo drzati na matricnoj
        izlazMatricna[i].value(0)

def StartLabirintGame(irq):
    global labirintPut,timerMat,gameStart,brojevi
    if gameStart:
        return
    gameStart=True
    print("POMJERAJ SE KROZ LAVIRINT SA 2 4 6 8")
    generisiPut()
    print(labirintPut) ##KASNIJE POSLATI DRUGOM IGRAČU KOJI JE PUT
    brojevi=[0,0,2,0] #Koliko vremena im daješ
    TimerOn()
    timerMat.init(mode=Timer.PERIODIC, period=50, callback=Labirint) ##Igrati se sa period



##########################################################################################
##PIN 20,21,22,26 se mogu reuse jer se koriste u matričnoj tastaturi

postavi([0,0,0,0])
buttons[0].irq(handler=StartPotenciometarGame,trigger=Pin.IRQ_FALLING)
 ##KASNIJE STAVITI DA NA BUTTON 0 RANDOM IGRICA POCNE SAD JE VISE BUTTON ZA TESTIRANJE
buttons[1].irq(handler=StartMatricnaGame,trigger=Pin.IRQ_FALLING)
buttons[2].irq(handler=StartLabirintGame,trigger=Pin.IRQ_FALLING)
print("Hello, Pi Pico W!")
while(1):
    sleep(1)

