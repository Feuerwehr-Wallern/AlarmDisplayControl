'''
Freiwillige Feuerwehr Wallern / Fraham
Infopoint Monitorsteuerung
Date: 12/2024
Author: HBM d.F. Stefan Pflüglmayer
Author: OBI Robert Kronawettleitner
'''

import os
import time
import logging
import subprocess
from GPIOHandler import MotionSensor_Handler, Button_Handler

# url and browser to show at the display
BROWSER_NAME = "firefox"  # select the browser here (e.g. 'firefox, or 'chromium')
INFOSCREEN_URL = "https://connected.rosenbauer.com/alarmmonitor/"
INFOSCREEN_URL = "https://time.is/New_York"  # just for a test

# GPIO setup
PIR_PIN = {    # GPIO pins for the HC-SR312 motion sensor's
   10 : [
      #None
      '10.0.0.60'     # examples
      #'localhost'
      ],
   11 : [
      #None
      '10.0.0.60'
      ]
}
EXT_PIN = {    # GPIO pins for a external alarm input
   2 : [
      #None
      '10.0.0.60'     # examples
      #'localhost'
      ],
   3 : [
      #None
      '10.0.0.60'
      ]
}

# timing parameters
CYCLE_TIME = 0.2           # loop time in seconds
TV_OVERRUN_TIME = 20       # time after tv should switch off in seconds
TV_ON_BLOCK_TIME = 3       # time to block switch tv on after switching off the tv in seconds
BROWSER_LOADING_TIME = 10  # wait to load the browser in seconds

# logging into a file
LOGFILE_NAME = f"infoscreen_logfile_{time.strftime('%Y')}.log"   # filename for the logfile
LOGFILE_PATH = os.path.join(os.path.dirname(__file__), "logfiles", LOGFILE_NAME)    # full file path

os.makedirs(os.path.dirname(LOGFILE_PATH), exist_ok=True)   # create a logfile folder if it doesn't exist

logging.basicConfig(
   format="%(asctime)s [%(levelname)s] %(message)s",
   level=logging.INFO,
   handlers=[
      logging.FileHandler(LOGFILE_PATH, 'a'),
      logging.StreamHandler()
   ]
)

# Function to turn HDMI output on
def turn_tv_on():
   if os.name == "posix":
      os.system(f"WAYLAND_DISPLAY=\"wayland-1\" wlr-randr --output HDMI-A-1 --on")
   elif os.name == "nt":
      pass  # todo

# Function to turn HDMI output off
def turn_tv_off():
   if os.name == "posix":
      os.system("WAYLAND_DISPLAY=\"wayland-1\" wlr-randr --output HDMI-A-1 --off")
   elif os.name == "nt":
      pass  # todo
   
# Function to open Firefox
def open_browser(browser:str, url:str, wait:int) -> bool:
   close_browser(browser)   # close browser if it is already open
   if os.name == "posix":
      open_browser_cmd = None
      if browser.lower() == "firefox":
         open_browser_cmd = f"WAYLAND_DISPLAY=\"wayland-1\" {browser.lower()} --new-window --kiosk-monitor wayland-1 --noerrdialogs --disable-infobars --disable-translate {url}"
      elif browser.lower() == "chromium":
         open_browser_cmd = f"WAYLAND_DISPLAY=\"wayland-1\" {browser.lower()} --new-window --kiosk --noerrdialogs --disable-infobars --disable-translate {url}"

      if open_browser_cmd is None:
         return False
      
      subprocess.Popen(
            open_browser_cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )

      time.sleep(wait)
      return True
         
   elif os.name == "nt":
      pass  # todo
   return False

# Function to close Firefox
def close_browser(browser:str):
   if os.name == "posix":
      os.system(f"pkill {browser.lower()}")
   elif os.name == "nt":
      pass  # todo


def main():
   tv_state = True            # init state of tv
   blocked = False            # init state blocking turn on
   start_time = time.time()   # start time in init state
   
   motion_detected = False
   motion_sensors = MotionSensor_Handler(PIR_PIN)

   ext_alarm_detected = False
   ext_alarm_sensors = Button_Handler(EXT_PIN)

   try:
      logging.info("TV infoscreen programm is started!")
      logging.info(f"{BROWSER_NAME.capitalize()} is displaying {INFOSCREEN_URL} in kiosk mode.")
      
      if open_browser(BROWSER_NAME, INFOSCREEN_URL, BROWSER_LOADING_TIME):
         logging.info(f"{BROWSER_NAME.capitalize()} is opened.")
      else:
         logging.warning(f"{BROWSER_NAME.capitalize()} is not opened!")

      while True:
         current_time = time.time()

         # update motions or external inputs
         motion_detected, motion_device = motion_sensors.getState()
         if motion_device:
            logging.info(f"Motion detected at {motion_device.pin} (pull_up={motion_device.pull_up}, host={motion_device.pin_factory.host}).")

         ext_alarm_detected, ext_device = ext_alarm_sensors.getState()
         if ext_device:
            logging.info(f"External input signal detected at {ext_device.pin} (pull_up={ext_device.pull_up}, host={ext_device.pin_factory.host}).")

         # timing algorithm to switch the tv
         if not tv_state and not blocked and (motion_detected or ext_alarm_detected):   # switch tv on
            turn_tv_on()
            logging.info("TV monitor is switched ON.")
            tv_state = True
            start_time = current_time
      
         elif tv_state and not blocked and (motion_detected or ext_alarm_detected):     # don't switch tv off until a motion or external alarm detected! 
            start_time = current_time

         if tv_state and (current_time - start_time >= TV_OVERRUN_TIME):  # switch tv off
            turn_tv_off()
            logging.info("TV monitor is switched OFF.")
            tv_state = False
            blocked = True
            start_time = current_time

         if blocked and (current_time - start_time >= TV_ON_BLOCK_TIME):
            blocked = False

         time.sleep(CYCLE_TIME)

   except KeyboardInterrupt:
      close_browser(BROWSER_NAME)
      logging.info(f"{BROWSER_NAME.capitalize()} browser is closing.")

   finally:
      # gpio cleanup
      del motion_sensors
      del ext_alarm_sensors
      logging.info("GPIO's cleaned up!")

      turn_tv_on()   # turn on tv befor stopping
      logging.info("TV infoscreen programm is stopped by user!")


if __name__ == "__main__":
   main()
