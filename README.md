# Wireless Communication System Node

Used by run crew to receive and acknowledge cues from the stage manager

## Hardware

- Raspberry Pi Zero 2 W
- [RGB backlight positive LCD 16x2 + extras - black on RGB](https://www.adafruit.com/product/398)
- [I2C Serial Interface Board](https://a.co/d/bbh3HwO)
- [Arcade Button with LED - 30mm](https://www.adafruit.com/product/3487)
- [MicroUSB Power Cable](https://www.adafruit.com/product/1995)

## Dependencies

You will need to install the following dependencies via the following commands:

```bash
sudo apt-get install python3-pandas
sudo apt-get install python3-netifaces
```

## Enabling/Disabling WiFi

Enabling:

```bash
sudo update-rc.d dhcpcd enable
sudo systemctl unmask wpa_supplicant.service
bash service wpa_supplicant start
```

Disabling:

```bash
bash service wpa_supplicant stop
sudo systemctl mask wpa_supplicant.service
sudo update-rc.d dhcpcd disable
```

## Setup of Code

1. Go to crontab, selecting the nano text editor if prompted:

    ```bash
    crontab -e
    ```

2. Scroll to the bottom and add the following line:

    ```bash
    @reboot sh /home/pi/Node/node_launcher.sh >/home/pi/cronlog 2>&1
    ```

3. Save the crontab by pressing ```CTRL+X``` then ```Enter```

4. Reboot to test:

    ```bash
    sudo reboot
    ```
