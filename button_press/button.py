import max7219
from machine import Pin, SPI, Timer

#dio što će ići u main slave pica:
spi = SPI(0, baudrate=10000000, sck=Pin(18), mosi=Pin(19))
ss = Pin(16, Pin.OUT)
display = max7219.Matrix8x8(spi, ss, 1)
display.fill(0)
display.show()

button=Pin(20,Pin.IN, Pin.PULL_UP)
timer=Timer()
time=0
dots=0

def button_defuse(seed=0):
    seed=seed%8
    def button_pressed(t):
        global timer
        timer.init(mode=Timer.PERIODIC, period=50, callback=dotting)

    def dotting(t):
        global time, dots, button, timer
        list = [[(3,1),(5,4),(0,2),(7,5),(2,3),(1,6),(4,6),(4,2),(3,5),(0,6)],
                [(0,1), (2,4), (5,3), (7,6), (3,2), (4,0), (6,7), (1,5), (6,2), (3,7)],
                [(1,0), (3,4), (6,5), (4,7), (2,1), (7,3), (0,5), (5,2), (1,7), (3,6)],
                [(2,0), (4,3), (6,1), (5,7), (1,2), (3,5), (0,4), (7,1), (2,6), (5,4)],
                [(0,3), (2,5), (4,6), (7,2), (3,1), (5,0), (6,4), (1,7), (5,6), (3,0)],
                [(1,3), (4,2), (7,5), (2,0), (6,3), (5,7), (3,6), (0,4), (2,7), (6,1)],
                [(3,2), (0,6), (5,1), (1,4), (7,3), (2,5), (4,0), (6,7), (3,4), (1,7)],
                [(2,3), (1,5), (4,6), (6,0), (7,4), (0,2), (5,7), (3,1), (6,5), (2,7)]
        ]
        time += 1
        if time%20 == 0:
            dots+=1
        display.pixel(list[seed][dots][0],list[seed][dots][1],1)
        display.show()
        if button.value()==0 and seed+1!=dots:
            display.fill(0)
            display.text('X',0,0,1)
            display.show()
            print("boom")
            timer.deinit()
        elif button.value()==0 and seed+1==dots:
            display.fill(1)
            display.show()
            print("gj")
            timer.deinit()
        elif dots>=9:
            display.fill(0)
            display.text('X',0,0,1)
            display.show()
            print("boom")
            timer.deinit()
    
    button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

button_defuse(7)
