'''
Freiwillige Feuerwehr Wallern / Fraham
Infopoint Monitorsteuerung
Date: 12/2024
Author: HBM d.F. Stefan Pflüglmayer
Author: OBI Robert Kronawettleitner
'''

import os
import signal
import time
import logging
import json
import subprocess
from dotenv import dotenv_values
from GPIOHandler import MotionSensor_Handler, Button_Handler

# load parameters from file
CONFIGFILE_PATH = os.path.join(os.path.dirname(__file__), ".env")
config = dotenv_values(CONFIGFILE_PATH)

# load gpio settings
PIR_PIN = json.loads(config['PIR_PIN'])
EXT_PIN = json.loads(config['EXT_PIN'])

# logging into a file
LOGFILE_NAME = config['LOGFILE_NAME'] + f"_{time.strftime('%Y')}.log"   # filename for the logfile
LOGFILE_PATH = os.path.join(os.path.dirname(__file__), "logfiles", LOGFILE_NAME)    # full file path

os.makedirs(os.path.dirname(LOGFILE_PATH), exist_ok=True)   # create a logfile folder if it doesn't exist

logging.basicConfig(
   format="%(asctime)s [%(levelname)s] %(message)s",
   handlers=[
      logging.FileHandler(LOGFILE_PATH, 'a'),
      logging.StreamHandler()
   ]
)
logging.root.setLevel(config['LOGLEVEL'].upper())

# helper for converting a string into a bool
def to_bool(s:str):
    return s.lower() == "true"

# catch termination signal here for gracefully shutdown
def signal_handler(signum, frame):
   exit(0)  # exit here
signal.signal(signal.SIGTERM, signal_handler)

# Function to select the source of the TV (just for HDMI-CEC controll!)
def select_tv_source(switching_method:str = "default", cec_addr:str = "0.0.0.0"):
    if os.name == "posix":
      if switching_method.lower() == "default":
         return  # do nothing, because you can select the source only in cec mode
      
      if switching_method.lower() == "cec":
         cmd = f"echo 'as {cec_addr}' | cec-client -s -d 1"

      else:
         logging.warning("Can not select the source, wrong TV switching method selected!")
         return
      
      logging.info("TV monitor input source is selected.")
      logging.debug(cmd)
      os.system(cmd)
      return
    
    elif os.name == "nt":
       pass  # todo

# Function to turn TV on
def turn_tv_on(switching_method:str = "default", way_disp:str = "wayland-0", cec_addr:str = "0.0.0.0"):
   if os.name == "posix":
      if switching_method.lower() == "default":
         cmd = f"WAYLAND_DISPLAY=\"{way_disp}\" wlr-randr --output HDMI-A-1 --on"

      elif switching_method.lower() == "cec":
         cmd = f"echo 'on {cec_addr}' | cec-client -s -d 1"

      else:
         logging.warning("Wrong TV switching method selected!")
         return
            
      logging.info("TV monitor is switched ON.")
      logging.debug(cmd)
      os.system(cmd)
      return
   
   elif os.name == "nt":
      pass  # todo

# Function to turn TV off
def turn_tv_off(switching_method:str = "default", way_disp:str = "wayland-0", cec_addr:str = "0.0.0.0"):
   if os.name == "posix":
      if switching_method.lower() == "default":
         cmd = f"WAYLAND_DISPLAY=\"{way_disp}\" wlr-randr --output HDMI-A-1 --off"

      elif switching_method.lower() == "cec":
         cmd = f"echo 'standby {cec_addr}' | cec-client -s -d 1"

      else:
         logging.warning("Wrong TV switching method selected!")
         return

      logging.info("TV monitor is switched OFF.")
      logging.debug(cmd)
      os.system(cmd)
      return
   
   elif os.name == "nt":
      pass  # todo

# Function to open Firefox
def open_browser(browser:str, url:str, wait:float, session_type:str, disp:str) -> bool:
   close_browser(browser)   # close browser if it is already open

   if not session_type:
      logging.warning("Can't open the browser, because no session type is given!")
      return False

   if not disp :
      logging.warning("Can't open the browser, because no display is given!")
      return False

   if os.name == "posix":
      if session_type == 'x11':
          cmd = f"DISPLAY=:{disp} "
      else:
         cmd = f"WAYLAND_DISPLAY=\"{disp}\" "   # default wayland

      if browser.lower() == "firefox":
         if session_type == 'x11':
            cmd += f"{browser.lower()} --kiosk"
         else:
            cmd += f"{browser.lower()} --kiosk-monitor {disp}"
      elif browser.lower() == "chromium":
         cmd += f"{browser.lower()} --kiosk"
      else:
         logging.warning("No or wrong browser selected!")
         return False

      cmd += " --new-window"
      cmd += " --noerrdialogs"
      cmd += " --disable-infobars"
      cmd += " --disable-translate"
      cmd += " --disable-restore-session-state"
      cmd += " --private-window"
   
      cmd += f" {url}"

      logging.info(f"{browser.capitalize()} is displaying {url} in kiosk mode.")
      logging.debug(cmd)
      subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )

      time.sleep(wait)

      logging.info(f"{browser.capitalize()} is opened.")
      return True
         
   elif os.name == "nt":
      pass  # todo

   logging.warning(f"{config['BROWSER_NAME'].capitalize()} is not opened!")
   return False

# Function to close Firefox
def close_browser(browser:str):
   if os.name == "posix":
      cmd = f"pkill {browser.lower()}"

      logging.info(f"{browser.capitalize()} browser is closed.")
      logging.debug(cmd)
      os.system(cmd)

   elif os.name == "nt":
      pass  # todo

# Function for searching the display
def find_display(session_type:str | None) -> str | None:
   if os.name == "posix":
      if session_type == 'x11':
         # todo find out the correct display
         logging.warning("Founded display: 0 (always display 0 when session type is x11!)")
         return '0'
      else:
         XDG_RUNTIME_DIR = f"/run/user/{os.getuid()}"

         if not os.path.isdir(XDG_RUNTIME_DIR):   # check if path exists
            logging.warning("No display founded, xdg runtime path does not exist!")
            return None
         
         for item in os.listdir(XDG_RUNTIME_DIR): # Scan for wayland display
            if item.startswith("wayland-") and len(item) == 9:
               logging.info(f"Founded display: {item}")
               return item
            
   elif os.name == "nt":
      pass    # todo

   logging.warning("No display founded!")
   return None    # if no display socket found, return None

# Function for searching the session
def find_session() -> str | None:
   if os.name == "posix":
      XDG_SESSION_TYPE = os.environ.get('XDG_SESSION_TYPE')
      if XDG_SESSION_TYPE:
         logging.info(f"Founded display session: {XDG_SESSION_TYPE}")
         return XDG_SESSION_TYPE
      else:
         logging.warning(f"No session founded, use \"wayland\" as default!")
         return 'wayland'   # return 'wayland' as default display here if the XDG_SESSION_TYPE isn't set
   
   elif os.name == "nt":
      pass    # todo

   logging.warning("No session founded!")
   return None


def main():
   tv_state = True            # init state of tv
   blocked = False            # init state blocking turn on
   never_switch_off = False   # init state tv never switch off by the programm
   start_time = time.time()   # start time in init state
   
   motion_sensors = MotionSensor_Handler(PIR_PIN)  # instance for motion sensors
   ext_alarm_sensors = Button_Handler(EXT_PIN)     # instance for external inputs

   try:
      logging.info("TV infoscreen programm is started!")

      # check if gpio pins are given or not (if True, the tv will never switch off by the programm)   
      if not PIR_PIN and not EXT_PIN:
         never_switch_off = True
         logging.info("TV will never switch of by the program, because no sensor pins are given!")

      # find session type and display here
      session_type = find_session()
      disp = find_display(session_type)

      # try to open browser in kiosk mode
      open_browser(config['BROWSER_NAME'], config['INFOSCREEN_URL'], float(config['BROWSER_LOADING_TIME']), session_type, disp)

      while True:
         current_time = time.time()

         # update motions and external inputs
         motion_detected = motion_sensors.getState()
         ext_alarm_detected = ext_alarm_sensors.getState()

         # timing algorithm to switch the tv
         if not tv_state and not blocked and (motion_detected or ext_alarm_detected):   # switch tv on
            turn_tv_on(config['TV_SWITCHING_METHOD'], disp)
            select_tv_source(config['TV_SWITCHING_METHOD'])
            if to_bool(config['BROWSER_REOPEN']):
               open_browser(config['BROWSER_NAME'], config['INFOSCREEN_URL'], float(config['BROWSER_LOADING_TIME']), session_type, disp)
            tv_state = True
            start_time = current_time
      
         elif tv_state and not blocked and (motion_detected or ext_alarm_detected or never_switch_off):     # don't switch tv off until a motion or external alarm detected! 
            start_time = current_time

         if tv_state and (current_time - start_time >= float(config['TV_OVERRUN_TIME'])):  # switch tv off
            turn_tv_off(config['TV_SWITCHING_METHOD'], disp)
            tv_state = False
            blocked = True
            start_time = current_time

         if blocked and (current_time - start_time >= float(config['TV_ON_BLOCK_TIME'])):
            blocked = False

         time.sleep(float(config['CYCLE_TIME']))

   except KeyboardInterrupt:
      logging.info("The programm is stopped by the user!")
   except SystemExit:
      logging.info("The programm is stopped by the System!")
   except Exception as error:
      logging.info("The programm is stopped by an unknown Event!")
      logging.error(error)

   finally:
      # close the browser
      close_browser(config['BROWSER_NAME'])
   
      # gpio cleanup
      del motion_sensors
      del ext_alarm_sensors
      logging.info("GPIO's cleaned up!")

      if not tv_state:
         turn_tv_on(config['TV_SWITCHING_METHOD'], disp)   # turn on tv befor stopping

      logging.info("TV infoscreen programm is stopped!")


if __name__ == "__main__":
   main()
