"""
AlarmDisplayControl GPIO Handler

"""

from gpiozero import MotionSensor, Button       # Doc: https://gpiozero.readthedocs.io/en/stable/index.html
from gpiozero.pins.pigpio import PiGPIOFactory  # use that for some external pins on a host ... Doc: https://gpiozero.readthedocs.io/en/stable/remote_gpio.html


class GPIO_Handler():
    def __init__(self):
        self.devices = {}               # store the device and the each state here
        self.loggedDeviceAction = []    # store the devices for logging

    def __del__(self):
        self.close()
        del self.devices

    def setState(self, callerDevice:Button):
        self.devices[callerDevice] = True
        self.loggedDeviceAction.append(callerDevice)

    def resetState(self, callerDevice:Button):
        self.devices[callerDevice] = False
   
    # returns the state true if any sensor is true and the last devices which are set
    def getState(self) -> tuple[bool, Button|MotionSensor|None]:
        state =  any([self.devices[device] for device in self.devices])

        if self.loggedDeviceAction:
            device = self.loggedDeviceAction
            self.loggedDeviceAction = []
            return state, device
        return state, []
    
    def close(self):
        for device in self.devices:
            device.close()


class Button_Handler(GPIO_Handler):
    def __init__(self, pins:dict):
        super().__init__()
        self.pins = pins
                
        for pin in self.pins:
            for ip in self.pins[pin]:
                if ip is None:
                    device = Button(pin, bounce_time=0.3)
                else:
                    device = Button(pin, bounce_time=0.3, pin_factory=PiGPIOFactory(host=ip))
                self.devices[device] = False

        for device in self.devices:
                device.when_pressed = self.setState      # func called when button pressed
                device.when_released = self.resetState   # func called when button released
                self.devices[device] = device.is_pressed # set init state here


class MotionSensor_Handler(GPIO_Handler):
    def __init__(self, pins:dict):
        super().__init__()
        self.pins = pins
                
        for pin in self.pins:
            for ip in self.pins[pin]:
                if ip is None:
                    device = MotionSensor(pin)
                else:
                    device = MotionSensor(pin, pin_factory=PiGPIOFactory(host=ip))
                self.devices[device] = False
    
        for device in self.devices:
            device.when_motion = self.setState              # func called when motion detected
            device.when_no_motion = self.resetState         # func called when no motion detected
            self.devices[device] = device.motion_detected   # set init state here
