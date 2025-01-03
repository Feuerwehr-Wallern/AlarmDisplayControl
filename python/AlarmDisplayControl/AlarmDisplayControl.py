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

# timing parameters
CYCLE_TIME = 0.2           # loop time in seconds
TV_OVERRUN_TIME = 20       # time after tv should switch off in seconds
TV_ON_BLOCK_TIME = 3       # time to block switch tv on after switching off the tv in seconds
BROWSER_LOADING_TIME = 10  # wait to load the browser in seconds

# GPIO setup
PIR_PIN = {    # GPIO pins for the HC-SR312 motion sensor's
   4 : [
      None          # 'None' use the local GPIO without pigpio
      #'localhost'   # 'localhost' use the local GPIO with pigpio
      #'10.0.0.60'    # 'xx.xx.xx.xx' use the remot GPIO with pigpio
      ],
   17 : [
      None
      #'localhost'
      #'10.0.0.60'
      ]
}
EXT_PIN = {    # GPIO pins for a external alarm input
   2 : [
      None          # 'None' use the local GPIO without pigpio
      #'localhost'   # 'localhost' use the local GPIO with pigpio
      #'10.0.0.60'    # 'xx.xx.xx.xx' use the remot GPIO with pigpio
      ],
   3 : [
      None
      #'localhost'
      #'10.0.0.60'
      ]
}

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

# Function for searching a wayland display
def find_wayland_display() -> str | None:
   time.sleep(4)  # todo, wait for available display
   
   path = f"/run/user/{os.getuid()}"

   if not os.path.isdir(path):   # check if path exists
      return None
   
   for item in os.listdir(path): # Scan for wayland display
      if item.startswith("wayland-") and len(item) == 9:
         return item
      pass

   return None # if no wayland socket found, return none

# Function to open Firefox
def open_browser(browser:str, url:str, wait:int) -> bool:
   close_browser(browser)   # close browser if it is already open
   if os.name == "posix":

      # check session_type
      session_type = os.environ.get('XDG_SESSION_TYPE')

      if session_type == 'wayland':
         way_disp = os.environ.get('WAYLAND_DISPLAY')
         cmd = f"WAYLAND_DISPLAY=\"{way_disp}\" "

      elif session_type == 'x11':
         pass # todo

      else:
         way_disp = find_wayland_display()
         if not way_disp:
            way_disp = "wayland-0"  # default
         
         cmd = f"WAYLAND_DISPLAY=\"{way_disp}\" "


      if browser.lower() == "firefox":
         if session_type == 'x11':
            cmd += f"{browser.lower()} --kiosk"
         else:
            cmd += f"{browser.lower()} --kiosk-monitor {way_disp}"
      elif browser.lower() == "chromium":
         cmd += f"{browser.lower()} --kiosk"
      else:
         return False   # no or wrong browser selected

      cmd += " --new-window"
      cmd += " --noerrdialogs"
      cmd += " --disable-infobars"
      cmd += " --disable-translate"
   
      cmd += f" {url}"

      logging.info(f"{browser.capitalize()} is displaying {url} in kiosk mode.")
      logging.info(f"{cmd}")
      subprocess.Popen(
            cmd,
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
   
   motion_sensors = MotionSensor_Handler(PIR_PIN)  # instance for motion sensors
   ext_alarm_sensors = Button_Handler(EXT_PIN)     # instance for external inputs

   try:
      logging.info("TV infoscreen programm is started!")
      
      # try to open browser in kiosk mode
      if open_browser(BROWSER_NAME, INFOSCREEN_URL, BROWSER_LOADING_TIME):
         logging.info(f"{BROWSER_NAME.capitalize()} is opened.")
      else:
         logging.warning(f"{BROWSER_NAME.capitalize()} is not opened!")

      while PIR_PIN or EXT_PIN:   # run while if PIR or EXT pins are defined
         current_time = time.time()

         # update motions or external inputs
         motion_detected = motion_sensors.getState()
         ext_alarm_detected = ext_alarm_sensors.getState()

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

      if not tv_state:
         turn_tv_on()   # turn on tv befor stopping
         logging.info("TV monitor is switched ON.")

      logging.info("TV infoscreen programm is stopped by user!")


if __name__ == "__main__":
   main()
