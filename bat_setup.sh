# Enable batman-adv
modprobe batman-adv

# Configure wlan0
iw dev wlan0 del
iw phy phy0 interface add wlan0 type ibss
ip link set up mtu 1532 dev wlan0
iw dev wlan0 ibss join wireless-communication-mesh 2432

# Configure wpa_supplicant
wpa_supplicant -B -i interface -c wpa_supplicant-adhoc.conf -D nl80211, wext

batctl if add wlan0
ip link set up dev bat0