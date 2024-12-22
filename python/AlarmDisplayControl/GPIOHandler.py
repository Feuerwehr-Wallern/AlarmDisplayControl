"""
AlarmDisplayControl GPIO Handler

"""

from gpiozero import MotionSensor, Button       # Doc: https://gpiozero.readthedocs.io/en/stable/index.html
from gpiozero.pins.pigpio import PiGPIOFactory  # use that for some external pins on a host ... Doc: https://gpiozero.readthedocs.io/en/stable/remote_gpio.html


class GPIO_Handler():
    def __init__(self):
        self.devices = {}   # store the device here
        self.state = {}     # store the states off all GPIO Devices
        self.loggedDeviceAction = []    # store the devices for logging

    def __del__(self):
        self.close()
        del self.devices

    def setState(self, caller:Button):
        self.state[caller] = True
        self.loggedDeviceAction.append(caller)

    def resetState(self, caller:Button):
        self.state[caller] = False
   
    # returns the state true if any sensor is true and the last devices which are set
    def getState(self) -> tuple[bool, Button|None]:
        state =  any([self.state[item] for item in self.state])
        
        if self.loggedDeviceAction:
            return state, self.loggedDeviceAction.pop(-1)
        return state, None
    
    def close(self):
        for pin in self.pins:
            for ip in self.pins[pin]:
                self.devices[pin][ip].close()


class Button_Handler(GPIO_Handler):
    def __init__(self, pins:dict):
        super().__init__()
        self.pins = pins
                
        for pin in self.pins:
            self.devices[pin] = {}
            for ip in self.pins[pin]:
                if ip is None:
                    self.devices[pin][ip] = Button(pin, bounce_time=0.3)
                else:
                    self.devices[pin][ip] = Button(pin, bounce_time=0.3, pin_factory=PiGPIOFactory(host=ip))
                
                self.devices[pin][ip].when_pressed = self.setState
                self.devices[pin][ip].when_released = self.resetState

                self.state[self.devices[pin][ip]] = self.devices[pin][ip].is_pressed # set init state here


class MotionSensor_Handler(GPIO_Handler):
    def __init__(self, pins:dict):
        super().__init__()
        self.pins = pins
                
        for pin in self.pins:
            self.devices[pin] = {}
            for ip in self.pins[pin]:
                if ip is None:
                    self.devices[pin][ip] = MotionSensor(pin)
                else:
                    self.devices[pin][ip] = MotionSensor(pin, pin_factory=PiGPIOFactory(host=ip))
                
                self.devices[pin][ip].when_motion = self.setState
                self.devices[pin][ip].when_no_motion = self.resetState

                self.state[self.devices[pin][ip]] = self.devices[pin][ip].motion_detected # set init state here
