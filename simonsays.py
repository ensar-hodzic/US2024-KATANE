from machine import Pin, Timer
import time
class SimonSays:
    def __init__(self, button_pins, led_pins, code):
        self.buttons = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in button_pins]
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
            output_index=0
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
    
    def play(self):
        while not self.solved:
            self.output_index=0
            self.input_index=0
            self.user_input=[]
            self.reset_leds()
            self.show_timer.init(period=500,mode=Timer.PERIODIC,callback=self.turn_on_led)#PRIKAZI SEKVENCU
            print("Ponovi sekvencu")
            while len(self.user_input) < len(self.code):
                time.sleep_ms(10)
            if self.user_input == self.code:
                print("Bravo!")
                for led in self.leds:
                    led.on()
                self.solved=True
            else:
                print("Ponovo.")
                self.greske+=1                
                

