from machine import Pin, Timer
import time
import random


class SimonSays:
    #vrijeme izmedju paljenja ledova u sekvenci
    T = 1000
    #unijeti brojeve pinova
    def __init__(self, button_pins:list, led_pins:list):
        self.buttons = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in button_pins]
        self.leds = [Pin(pin, Pin.OUT) for pin in led_pins]
        
        
        self.code = [random.randint(0, len(led_pins)-1) for _ in range(5)]
        self.output_index=0
        self.input_index=0
        self.user_input=[]
        self.showingSequence = False
        self.DEBOUNCE_TIME = 200
        self.last_interrupt_time = 0
        self.solved=False
        self.greske=0
        for button in self.buttons:
            button.irq(trigger=Pin.IRQ_RISING,handler=self.button_handler)
        self.checkingInput = Timer(period=200,mode=Timer.PERIODIC,callback=self.checkInput)
        self.show_timer = Timer(period=self.T,mode=Timer.PERIODIC,callback=self.turn_on_led)#PRIKAZI SEKVENCU
        #vrijeme izmedju prikazivanja sekvence
        self.prikazujSekvencu = Timer(period=self.T*len(self.code)*2,mode=Timer.PERIODIC,callback=self.prikaziSekvencu)

    def prikaziSekvencu(self,pin):
        if  not self.user_input and not self.solved: 
            self.show_timer.init(period=self.T,mode=Timer.PERIODIC,callback=self.turn_on_led)#PRIKAZI SEKVENCU
        
    
    def checkInput(self,pin):
        if len(self.user_input)==len(self.code):    
            if  self.user_input == self.code:
                for led in self.leds:
                    led.on()
                self.solved=True
                pin.deinit()
            else:
                self.output_index=0
                self.input_index=0
                self.user_input=[]
                for led in self.leds:
                    led.off()
                self.greske = self.greske + 1
                prikazujGresku = Timer(period=250,mode = Timer.PERIODIC,callback = self.prikaziGresku)
        
    def button_handler(self,pin):
        if not self.showingSequence :
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.last_interrupt_time) > self.DEBOUNCE_TIME:
                self.last_interrupt_time = current_time
                if self.input_index < len(self.code):
                    for i, button in enumerate(self.buttons):
                        if button is pin:
                            self.user_input.append(i)
                    self.input_index += 1    

    
    def turn_on_led(self, pin):
        if self.output_index == 0:
            self.showingSequence=True
            self.leds[self.code[self.output_index]].on()
            self.output_index = self.output_index + 1
        elif self.output_index < len(self.code):
            self.leds[self.code[self.output_index-1]].off()
            self.leds[self.code[self.output_index]].on()
            self.output_index = self.output_index + 1
        else:
            self.leds[self.code[self.output_index-1]].off()
            self.output_index=0
            self.showingSequence = False
            pin.deinit()
    
    prikazujeGresku=False
    def prikaziGresku(self,pin):
        if self.output_index==4:
            self.output_index=0
            for led in self.leds:
                led.off()
            prikazujeGresku = False
            pin.deinit()
        else:
            self.output_index+=1
            for led in self.leds:
                led.toggle()
                    
            