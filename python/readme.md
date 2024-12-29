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
### Method 1: using autostart folder
1.  Create a autostart folder if it doesen't exists:
    ```env
    sudo mkdir /home/pi/.config/autostart
    ```

2.  Create a new .desktop file:
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
    Save with `Ctrl`+`x`.

### Method 2: using systemctl
1.  Create a new .service file:
    ```env
    sudo nano /etc/systemd/system/infoscreen.service
    ```

2.  Copy the following code into the infoscreen.service file:
    ```env
    [Unit]
    Description=AlarmDisplayControl
    After=graphical.target

    [Service]
    Type=idle
    User=pi
    Environment="XDG_RUNTIME_DIR=/run/user/1000"
    WorkingDirectory=/home/pi/Desktop/AlarmDisplayControl/python/AlarmDisplayControl
    ExecStart=/usr/bin/python AlarmDisplayControl.py

    [Install]
    WantedBy=graphical.target
    ```
    Save with `Ctrl`+`x`.

3.  Check status, start, stop, ...
    ```env
    sudo systemctl status infoscreen
    ```

Useful links for systemctl:
https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units#editing-unit-files
https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files

## Hide Cursor (Raspberry PI)
..

## Some useful links
XDG Base Directory Specification: https://specifications.freedesktop.org/basedir-spec/latest/

