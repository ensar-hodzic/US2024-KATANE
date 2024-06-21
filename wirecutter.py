from machine import Pin, Timer

class WireCutter:
    def __init__(self,outputs:list,inputs:list,valid_to_cut:list,inOrder:bool):

        self.outputs = [Pin(pin, Pin.OUT) for pin in outputs]
        self.inputs = [Pin(pin, Pin.IN) for pin in inputs]
        self.valid_to_cut= [Pin(pin,Pin.IN) for pin in valid_to_cut]
        self.inOrder=inOrder
        for output in self.outputs:
            output.on()
        self.timer=Timer(-1)
        self.solved=False
        self.greske=0
        self.timer.init(period=100,mode=Timer.PERIODIC,callback=self.CheckWires)
        for pin in self.inputs:
            pin.irq(trigger=Pin.IRQ_FALLING,handler=self.CheckWires)
        self.checker=Timer(-1)
        self.checker(period=100,mode=Timer.PERIODIC,callback=self.checkSolved)
    
    def CheckWires(self,pin):
        if pin in self.valid_to_cut:
            if self.inOrder:
                for wire in self.valid_to_cut:
                    if wire is pin:
                        self.valid_to_cut.remove(wire)
                        break
                    else:
                        if wire.value()==1:
                            self.greske+=1                
        else:
            self.valid_to_cut.remove(pin)
            self.greske+=1
            
    def checkSolved(self,pin):
        if not self.valid_to_cut:
            self.solved=True