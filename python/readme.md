# python adaptation of arduino code


## Used GPIO Libary
Doc:  https://gpiozero.readthedocs.io/

MotionSensor: https://gpiozero.readthedocs.io/en/latest/api_input.html#gpiozero.MotionSensor
Button: https://gpiozero.readthedocs.io/en/latest/api_input.html#gpiozero.Button

### Raspberry Pi Pinout
A GPIO reference can be accessed on your Raspberry Pi by opening a terminal window and running the command
```env
pinout
```
This tool is provided by the GPIO Zero Python library, which is installed by default in Raspberry Pi OS.

Other Methods:
https://pinout.xyz/
https://gpiozero.readthedocs.io/en/latest/api_input.html#gpiozero.Button

## Remote GPIO
You can use remote GPIO's from other devices in the network.
If you need this, follow the instructions: https://gpiozero.readthedocs.io/en/latest/remote_gpio.html

## Autostart (Raspberry PI)
### Using autostart
1.  Create a autostart folder if it doesen't exists:
    ```env
    sudo mkdir /home/pi/.config/autostart
    ```

2.  Create a .desktop file:
    ```env
    sudo nano /home/pi/.config/autostart/infoscreen.desktop
    ```

3.  Copy the following code into the infoscreen.desktop file:
    ```env
    [Desktop Entry]
    Type=Application
    Name=AlarmDisplayControl-Autostart
    Exec=/usr/bin/python /home/pi/Desktop/AlarmDisplayControl/python/AlarmDisplayControl/AlarmDisplayControl.py
    ```
    Save with ctrl+x

### Using systemd

## Hide Cursor (Raspberry PI)
..

## Some useful links
XDG Base Directory Specification: https://specifications.freedesktop.org/basedir-spec/latest/

