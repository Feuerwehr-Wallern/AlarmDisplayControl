import RPi.GPIO as GPIO
import os
import time
import subprocess
# GPIO setup
PIR_PIN = 18 # GPIO pin for the HC-SR312 motion sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
# Function to turn HDMI output off
def turn_hdmi_off():
   subprocess.run(["wlr-randr","--output","HDMI-A-1","--off"])
   print("[DEBUG] HDMI output turned OFF.")
# Function to turn HDMI output on and display Google
def turn_hdmi_on():
   # Launch Firefox in fullscreen mode to display www.google.at
   subprocess.Popen(["firefox", "--kiosk", "https://connected.rosenbauer.com/alarmmonitor/"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
   print("[DEBUG] Displaying https://connected.rosenbauer.com/alarmmonitor/ in kiosk mode with Firefox.")
   # Turn HDMI on
   subprocess.run(["wlr-randr","--output","HDMI-A-1","--on"])
   print("[DEBUG] HDMI output turned ON.")
   # Ensure the display wakes up
   time.sleep(1)
   subprocess.run(["/bin/fbset", "-depth", "8"])
   subprocess.run(["/bin/fbset", "-depth", "16"])
# Function to close Firefox
def close_browser():
   subprocess.run(["pkill", "firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
   print("[DEBUG] Closed Firefox browser.")
# Timer and state variables
hdmi_on = False
last_motion_time = 0
timeout = 60  # 15 minutes in seconds
try:
   turn_hdmi_on()
   hdmi_on=True
   last_motion_time=time.time()
   #print("[DEBUG] Program started. Waiting for motion...")
   while True:
       motion_detected = GPIO.input(PIR_PIN)
       current_time = time.time()
       if motion_detected == GPIO.HIGH:
           print(f"[DEBUG] Motion detected at {time.strftime('%Y-%m-%d %H:%M:%S')}!")
           if not hdmi_on:
               #print("[DEBUG] HDMI is currently OFF. Turning ON and displaying Google...")
               turn_hdmi_on()
               hdmi_on = True
           last_motion_time = current_time
       # Check if the 15-minute timeout has passed
       if hdmi_on and (current_time - last_motion_time > timeout):
           print("[DEBUG] No motion detected for 15 minutes. Turning HDMI OFF and closing browser...")
           close_browser()
           turn_hdmi_off()
           hdmi_on = False
       # Add a short delay to avoid high CPU usage
       time.sleep(1)
except KeyboardInterrupt:
   print("[DEBUG] Program stopped by user.")
   if hdmi_on():
       close_browser()
finally:
   GPIO.cleanup()
   print("[DEBUG] GPIO cleaned up.")
