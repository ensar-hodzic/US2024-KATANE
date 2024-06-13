import random
import time
import max7219
from machine import Pin, SPI,  Timer

# SPI NE MOŽE BITI SVAKI PIN, radi za 10 i 11
spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11)) #DIN(10) CLK(11)

# Initialize CS (Chip Select) pin
cs = Pin(15, Pin.OUT)   #CHIP SELECT

buttons=[Pin(i,Pin.IN) for i in range(4)]

# Create display instance
display = max7219.Matrix8x8(spi, cs, 1)   #GLOBALNAAAA


# putanja dole lijevo gore desno
DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]     #KONSTANTA

def custom_shuffle(directions):
    n = len(directions)
    for i in range(n-1, 0, -1):
        j = random.randint(0, i)
        directions[i], directions[j] = directions[j], directions[i]

def generate_maze():
    random.seed(time.ticks_ms())    #U ZAVISNOSTI KAD KLIKNE GENERIŠE SE RANDOM
    
    maze = [[True] * 8 for _ in range(8)]
    start = (1, 1)
    end_options = [(6, 7), (7, 6)] 
    end = random.choice(end_options)

    def in_bounds(x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def carve_passages(x, y):
        directions = DIRECTIONS[:]
        custom_shuffle(directions)
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
    create_direct_path(maze, start, end)

    # Dodaj zidove
    for i in range(8):
        maze[0][i] = True
        maze[7][i] = True
    for i in range(8):
        maze[i][0] = True
        maze[i][7] = True
    maze[end[1]][end[0]] = False
    return maze, end

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

def print_maze(maze):
    for row in maze:
        print(" ".join('1' if cell else '0' for cell in row))

time.sleep(0.123) #random seed


##AA GLOBALNE
igracx=1
igracy=1
igracBlic=Timer(-1)
maze, end = generate_maze()
debouncer=0

def Provjeri():
    global igracx,igracy,end
    if end[1]==igracx and end[0]==igracy:
        zavrsiLabirint()


def Desno(irq):
    global igracx,igracy,end,maze,debouncer
    if time.ticks_ms()-debouncer<300:
        return
    debouncer=time.ticks_ms()
    if maze[igracx][igracy+1]==False:
        maze[igracx][igracy]=0
        igracy+=1
        Provjeri()
        display.display_matrix(maze)
    else:
        print("BONK")

def Gore(irq):
    global igracx,igracy,end,maze,debouncer
    if time.ticks_ms()-debouncer<300:
        return
    debouncer=time.ticks_ms()
    if maze[igracx-1][igracy]==False:
        maze[igracx][igracy]=0
        igracx-=1
        Provjeri()
        display.display_matrix(maze)
    else:
        print("BONK")


def Lijevo(irq):
    global igracx,igracy,end,maze,debouncer
    if time.ticks_ms()-debouncer<300:
        return
    debouncer=time.ticks_ms()
    if maze[igracx][igracy-1]==False:
        maze[igracx][igracy]=0
        igracy-=1
        Provjeri()
        display.display_matrix(maze)
    else:
        print("BONK")

def Dolje(irq):
    global igracx,igracy,end,maze,debouncer
    if time.ticks_ms()-debouncer<300:
        return
    debouncer=time.ticks_ms()
    if maze[igracx+1][igracy]==False:
        maze[igracx][igracy]=0
        igracx+=1
        Provjeri()
        display.display_matrix(maze)
    else:
        print("BONK")

buttons[0].irq(handler=Lijevo,trigger=Pin.IRQ_RISING)
buttons[1].irq(handler=Gore,trigger=Pin.IRQ_RISING)
buttons[2].irq(handler=Dolje,trigger=Pin.IRQ_RISING)
buttons[3].irq(handler=Desno,trigger=Pin.IRQ_RISING)

def prikaziIgraca(tim):
    global maze,igracx,igracy
    maze[igracx][igracy] = not maze[igracx][igracy]
    display.display_matrix(maze)


def startLabirint():
    global maze,end,igracx,igracy
    maze, end = generate_maze()
    igracx=1
    igracy=1
    igracBlic.init(mode=Timer.PERIODIC, period=500, callback=prikaziIgraca)


def zavrsiLabirint():
    global igracBlic,maze
    igracBlic.deinit()
    for i in range(8):
        for j in range(8):
            maze[i][j]=False
    display.display_matrix(maze)
    print("Svaka ti dala")


startLabirint()

while True:
    time.sleep(2)
