import random
import time
import max7219
from machine import Pin, SPI,  Timer

class Labirint:
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)] 
    
    #display: spi, SCK, MOSI, CS

    def __init__(self, buttons:list, display_pins:list):
        self.buttons = [Pin(i,Pin.IN, Pin.PULL_UP) for i in buttons]
        self.solved  = False
        self.strikes = 0

        spi = SPI(display_pins[0], baudrate=10000000, polarity=0, phase=0, 
                    sck=Pin(display_pins[1]), mosi=Pin(display_pins[2])) #DIN(18) CLK(19) 
        # Initialize CS (Chip Select) pin
        cs = Pin(display_pins[3], Pin.OUT)   #CHIP SELECT i spi su hardcodirani pinovi!

        self.display = max7219.Matrix8x8(self.spi, self.cs, 1)  


        self.igracx=1
        self.igracy=1
        self.igracBlic=Timer(-1)
        self.maze, self.end = self.generate_maze()
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
        print("Svaka ti dala")

    def prikaziIgraca(self, tim):
        self.maze[self.igracx][self.igracy] = not self.maze[self.igracx][self.igracy]
        self.display.display_matrix(self.maze)

    def startLabirint(self):
        self.maze, self.end = self.generate_maze()
        self.igracx=1
        self.igracy=1
        self.igracBlic.init(mode=Timer.PERIODIC, period=500, callback=self.prikaziIgraca)

    @staticmethod
    def custom_shuffle(directions):
        n = len(directions)
        for i in range(n-1, 0, -1):
            j = random.randint(0, i)
            directions[i], directions[j] = directions[j], directions[i]


    @staticmethod
    def generate_maze(): 
    """
    Ovo trenutno generira nasumicni lavirint, i prikazuje isti na ekran
    Ja mislim da je poenta da postoje 8 mogucih lavirinata.
    NE prikazuju se na ekran, vec je u manualu izgled lavirinta, 
    a na ekran se samo prikaze trenutna pozicija.
    TODO: generate_maze(state) -> MOGUCI_LAVIRINTI[state]
    """
        random.seed(time.ticks_ms())    #U ZAVISNOSTI KAD KLIKNE GENERIŠE SE RANDOM
        
        maze = [[True] * 8 for _ in range(8)]
        start = (1, 1)
        end_options = [(6, 7), (7, 6)] 
        end = random.choice(end_options)

        def in_bounds(x, y):
            return 0 <= x < 8 and 0 <= y < 8

        def carve_passages(x, y):
            directions = Labirint.DIRECTIONS[:]
            Labirint.custom_shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + 2 * dx, y + 2 * dy
                if in_bounds(nx, ny) and maze[ny][nx]:
                    maze[y + dy][x + dx] = False
                    maze[ny][nx] = False
                    carve_passages(nx, ny)

        # Startna pozicija
        maze[start[1]][start[0]] = False

        # Put od starta
        carve_passages(start[0], start[1])
        
        # Direktan put
        Labirint.create_direct_path(maze, start, end)

        # Dodaj zidove
        for i in range(8):
            maze[0][i] = True
            maze[7][i] = True
        for i in range(8):
            maze[i][0] = True
            maze[i][7] = True
        maze[end[1]][end[0]] = False
        return maze, end


    def Provjeri(self):
        if self.end[1]==self.igracx and self.end[0]==self.igracy:
            self.zavrsiLabirint()


    def Desno(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx][self.igracy+1]==False:
            self.maze[self.igracx][self.igracy]=0
            self.igracy+=1
            self.Provjeri()
            self.display.display_matrix(self.maze)
        else:
            print("BONK")
            self.strikes += 1

    def Gore(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx-1][self.igracy]==False:
            self.maze[self.igracx][self.igracy]=0
            self.igracx-=1
            self.Provjeri()
            self.display.display_matrix(self.maze)
        else:
            print("BONK")
            self.strikes += 1


    def Lijevo(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx][self.igracy-1]==False:
            self.maze[self.igracx][self.igracy]=0
            self.igracy-=1
            self.Provjeri()
            self.display.display_matrix(self.maze)
        else:
            print("BONK")
            self.strikes += 1

    def Dolje(self,irq):
        if time.ticks_ms()-self.debouncer<300:
            return
        self.debouncer=time.ticks_ms()
        if self.maze[self.igracx+1][self.igracy]==False:
            self.maze[self.igracx][self.igracy]=0
            self.igracx+=1
            self.Provjeri()
            self.display.display_matrix(self.maze)
        else:
            print("BONK")
            self.strikes += 1

    def get_strikes(self) 
        return self.strikes

    @staticmethod
    def create_direct_path(maze, start, end):
        sx, sy = start
        ex, ey = end

        # Pazi da se može doći do kraja
        if ex == 7:  # End at (7, 6)
            for y in range(sy, ey + 1):
                maze[y][sx] = False
            for x in range(sx, ex + 1):
                maze[ey][x] = False
        else:  # End at (6, 7)
            for x in range(sx, ex + 1):
                maze[sy][x] = False
            for y in range(sy, ey + 1):
                maze[y][ex] = False

    @staticmethod
    def print_maze(maze):
        for row in maze:
            print(" ".join('1' if cell else '0' for cell in row))
