"""
Get the mac address of a node
"""

# Import the ifaddresses function from netifaces to get the wlan0 mac address of the node
from netifaces import ifaddresses, AF_LINK

# Define the get__mac function to get the MAC address of a node
def get_mac() -> str:
    """Get the MAC address of wlan0 of a node."""
    return ifaddresses('wlan0')[AF_LINK][0]['addr']