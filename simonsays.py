from machine import Pin, Timer
import time
class SimonSays:
    #vrijeme izmedju paljenja ledova u sekvenci
    T = 1000
    #unijeti brojeve pinova
    def __init__(self, button_pins:list, led_pins:list, code:list):
        self.buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in button_pins]
        self.leds = [Pin(pin, Pin.OUT) for pin in led_pins]
        self.code = code
        self.show_timer=Timer(-1)
        self.output_index=0
        self.input_index=0
        self.user_input=[]
        self.DEBOUNCE_TIME = 200
        self.last_interrupt_time = 0
        self.solved=False
        self.greske=0
        for button in self.buttons:
            button.irq(trigger=Pin.IRQ_RISING,handler=self.button_handler)
        self.checkingInput=Timer(-1)
        self.prikazujSekvencu=Timer(-1)
        
        self.checkingInput.init(period=200,mode=Timer.PERIODIC,callback=self.checkInput)
        self.show_timer.init(period=self.T,mode=Timer.PERIODIC,callback=self.turn_on_led)#PRIKAZI SEKVENCU
        #vrijeme izmedju prikazivanja sekvence
        self.prikazujSekvencu.init(period=self.T*len(self.code)*2,mode=Timer.PERIODIC,callback=self.prikaziSekvencu)

    def prikaziSekvencu(self,pin):
        if  not self.user_input and not self.solved: 
            self.show_timer.init(period=self.T,mode=Timer.PERIODIC,callback=self.turn_on_led)#PRIKAZI SEKVENCU
        
    
    def checkInput(self,pin):
        if len(self.user_input)==len(self.code):    
            if  self.user_input == self.code:
                print("Bravo!")
                for led in self.leds:
                    led.on()
                self.solved=True
                pin.deinit()
            else:
                self.output_index=0
                self.input_index=0
                self.user_input=[]
                self.reset_leds()
                print("Ponovo.")
                self.greske = self.greske + 1
        
    def button_handler(self,pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_interrupt_time) > self.DEBOUNCE_TIME:
            self.last_interrupt_time = current_time
            if self.input_index < len(self.code):
                for i, button in enumerate(self.buttons):
                    if button is pin:
                        self.user_input.append(i)
                self.input_index += 1    

    def reset_leds(self):
        for led in self.leds:
            led.off()
    
    def turn_on_led(self, pin):
        if self.output_index == 0:
            self.leds[self.code[self.output_index]].on()
            self.output_index = self.output_index + 1
        elif self.output_index < len(self.code):
            self.leds[self.code[self.output_index-1]].off()
            self.leds[self.code[self.output_index]].on()
            self.output_index = self.output_index + 1
        else:
            self.leds[self.code[self.output_index-1]].off()
            self.output_index=0
            pin.deinit()

    def ShowFailure(self,pin):
        if self.output_index==4:
            self.output_index=0
            self.reset_leds()
            pin.deinit()
        else:
            self.output_index+=1
            for led in self.leds:
                led.value(not led.value())
                    
                

#game = SimonSays([0,1,2,3],[4,5,6,7],[0,1,2,3])