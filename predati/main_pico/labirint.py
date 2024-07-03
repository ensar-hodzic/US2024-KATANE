import random
import time
import max7219
import gc
from machine import Pin, SPI,  Timer

class Labirint:
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
   
    #display: spi, SCK, MOSI, CS

    def __init__(self, buttons:list, display_pins:list,state):
        self.buttons = [Pin(i,Pin.IN, Pin.PULL_UP) for i in buttons]
        self.solved  = False
        self.strikes = 0
        self.seed=state%8
        self.spi = SPI(display_pins[0], baudrate=10000000, polarity=0, phase=0,
                    sck=Pin(display_pins[1]), mosi=Pin(display_pins[2])) #DIN(18) CLK(19)
        # Initialize CS (Chip Select) pin
        self.cs = Pin(display_pins[3], Pin.OUT)   #CHIP SELECT i spi su hardcodirani pinovi!

        self.display = max7219.Matrix8x8(self.spi, self.cs, 1)  

        self.stanjeIgrac=True
        self.igracx=1
        self.igracy=1
        self.igracBlic=Timer(-1)
        self.debouncer=0
        
        self.buttons[0].irq(handler=self.Lijevo,trigger=Pin.IRQ_RISING)
        self.buttons[1].irq(handler=self.Gore,trigger=Pin.IRQ_RISING)
        self.buttons[2].irq(handler=self.Dolje,trigger=Pin.IRQ_RISING)
        self.buttons[3].irq(handler=self.Desno,trigger=Pin.IRQ_RISING)

        self.startLabirint()


    def zavrsiLabirint(self):
        self.igracBlic.deinit()
        for i in range(8):
            for j in range(8):
                self.maze[i][j]=False
        self.display.display_matrix(self.maze)
        self.solved  = True

    def prikaziIgraca(self, tim):
        #print(gc.mem_free())
        gc.collect()
        self.stanjeIgrac= not self.stanjeIgrac
        self.display.pixel(self.igracx,self.igracy,self.stanjeIgrac)
        self.display.show()



    def startLabirint(self):
        self.generate_maze()
        self.upaliKraj()
        self.igracx=1
        self.igracy=1
        self.igracBlic.init(mode=Timer.PERIODIC, period=500, callback=self.prikaziIgraca)



    def generate_maze(self):
        if self.seed==0:
            self.maze=[
                 [True, True, True, True, True, True, True, True],
                 [True, False, True, False, False, False, False, True],
                 [True, False, True, False, False, False, False, True],
                 [True, False, False, False, True, True, False, True],
                 [True, False, True, False, False, True, False, True],
                 [True, False, True, True, True, True, False, True],
                 [True, False, False, False, False, True, False, False],
                 [True, True, True, True, True, True, True, True]
                ]
        elif self.seed==1:
            self.maze=[
                 [True, True, True, True, True, True, True, True],
                 [True, False, False, False, False, False, False, True],
                 [True, True, True, True, True, True, False, True],
                 [True, False, False, False, False, True, False, True],
                 [True, False, True, True, False, False, False, True],
                 [True, False, False, True, True, True, True, True],
                 [True, False, False, False, False, False, False, False],
                 [True, True, True, True, True, True, True, True]
                ]
        elif self.seed==2:
            self.maze=[
                    [True, True, True, True, True, True, True, True],
                    [True, False, False, False, False, False, False, True],
                    [True, False, True, True, True, True, False, True],
                    [True, False, False, False, False, False, False, True],
                    [True, False, True, True, False, True, True, True],
                    [True, False, True, True, False, True, True, True],
                    [True, False, False, True, False, False, False, False],
                    [True, True, True, True, True, True, True, True]
                    ]
        elif self.seed==3:
            self.maze=[
                 [True, True, True, True, True, True, True, True],
                 [True, False, True, False, False, False, False, False],
                 [True, False, True, False, False, True, True, True],
                 [True, False, False, False, True, True, False, True],
                 [True, False, True, False, False, False, False, True],
                 [True, False, True, True, True, True, True, True],
                 [True, False, False, False, False, False, False, True],
                 [True, True, True, True, True, True, True, True]
                ]
        elif self.seed==4:
            self.maze=[
                 [True, True, True, True, True, True, True, True],
                 [True, False, False, False, False, False, False, True],
                 [True, True, True, True, False, True, False, True],
                 [True, False, False, False, False, True, False, True],
                 [True, False, True, True, True, True, False, True],
                 [True, False, True, False, True, True, False, True],
                 [True, False, False, False, True, False, False, True],
                 [True, True, True, False, True, True, True, True]
                ]
        elif self.seed==5:
            self.maze=[
                 [True, True, True, True, True, True, True, True],
                 [True, False, True, False, False, False, False, True],
                 [True, False, True, False, True, True, False, True],
                 [True, False, False, False, True, False, False, True],
                 [True, True, True, True, True, False, True, True],
                 [True, False, True, True, True, False, False, True],
                 [True, False, False, False, False, False, False, True],
                 [True, False, True, True, True, True, True, True]
                ]
        elif self.seed==6:
            self.maze=[
                 [True, True, True, True, True, True, True, True],
                 [True, False, True, False, False, False, False, True],
                 [True, False, False, False, True, True, False, True],
                 [True, True, True, True, True, True, False, True],
                 [False, False, True, False, False, False, False, True],
                 [True, False, True, True, True, True, False, True],
                 [True, False, False, False, False, False, False, True],
                 [True, True, True, True, True, True, True, True]
                ]
        elif self.seed==7:
            self.maze=[
                 [True, True, True, False, True, True, True, True],
                 [True, False, True, False, False, False, False, True],
                 [True, False, True, True, True, True, False, True],
                 [True, False, False, False, False, True, False, True],
                 [True, False, True, True, False, False, False, True],
                 [True, False, False, False, True, True, True, True],
                 [True, False, True, False, False, False, False, True],
                 [True, True, True, True, True, True, True, True]
                ]
    def upaliKraj(self):
        for i in range(8):
            if not self.maze[i][0]:
                self.display.pixel(i,0,1)
                self.display.show()
                return
            if not self.maze[i][7]:
                self.display.pixel(i,7,1)
                self.display.show()
                return
            if not self.maze[0][i]:
                self.display.pixel(0,i,1)
                self.display.show()
                return
            if not self.maze[7][i]:
                self.display.pixel(7,i,1)
                self.display.show()  
                return  
    def Provjeri(self):
        if self.igracx==0 or self.igracy==0 or self.igracx==7 or self.igracy==7:
            self.zavrsiLabirint()


    def Gore(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx][self.igracy+1]==False:
            self.display.pixel(self.igracx,self.igracy,False)
            self.igracy+=1
            self.Provjeri()
        else:
            self.strikes += 1

    def Desno(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx-1][self.igracy]==False:
            self.display.pixel(self.igracx,self.igracy,False)
            self.igracx-=1
            self.Provjeri()
        else:
            self.strikes += 1


    def Dolje(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx][self.igracy-1]==False:
            self.display.pixel(self.igracx,self.igracy,False)
            self.igracy-=1
            self.Provjeri()
        else:
            self.strikes += 1

    def Lijevo(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx+1][self.igracy]==False:
            self.display.pixel(self.igracx,self.igracy,False)
            self.igracx+=1
        else:
            self.strikes += 1

    def get_strikes(self):
        return self.strikes
    def deinit(self):
        self.zavrsiLabirint()

